"""
Trains an EfficientNetB0 transfer-learning model on the PlantVillage dataset (38 classes).

Expected dataset layout (Kaggle "New Plant Diseases Dataset (Augmented)" style):

    ml_model/dataset/
        train/
            Apple___Apple_scab/*.jpg
            Apple___Black_rot/*.jpg
            ...
        valid/
            Apple___Apple_scab/*.jpg
            ...

Usage:
    python train.py --epochs 15 --fine-tune-epochs 10
"""
import argparse
import json
import logging
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SAVED_MODEL_DIR = SCRIPT_DIR / "saved_model"


def build_augmentation() -> tf.keras.Sequential:
    """Geometric/color augmentation applied only to the training split (see build_datasets)."""
    return tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.15),
            layers.RandomZoom(0.15),
            layers.RandomContrast(0.15),
            layers.RandomTranslation(0.1, 0.1),
        ],
        name="augmentation",
    )


def build_datasets(
    data_dir: Path, image_size: int, batch_size: int
) -> Tuple[tf.data.Dataset, tf.data.Dataset, List[str]]:
    """Loads train/valid splits from disk, augments the training split, and applies
    EfficientNet's preprocess_input to both — matching exactly what the backend's
    PredictionService does at inference time (see app/services/prediction_service.py).
    """
    train_dir = data_dir / "train"
    valid_dir = data_dir / "valid"

    if not train_dir.exists() or not valid_dir.exists():
        raise FileNotFoundError(
            f"Expected '{train_dir}' and '{valid_dir}' to exist. "
            "Download the PlantVillage dataset and organize it into train/ and valid/ subfolders."
        )

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=True,
        seed=42,
    )
    valid_ds = tf.keras.utils.image_dataset_from_directory(
        valid_dir,
        image_size=(image_size, image_size),
        batch_size=batch_size,
        label_mode="categorical",
        shuffle=False,
    )

    class_names = train_ds.class_names
    logger.info("Discovered %d classes", len(class_names))

    augmentation = build_augmentation()
    autotune = tf.data.AUTOTUNE

    def augment_and_preprocess(images: tf.Tensor, labels: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
        images = augmentation(images, training=True)
        return preprocess_input(images), labels

    def preprocess_only(images: tf.Tensor, labels: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
        return preprocess_input(images), labels

    train_ds = train_ds.map(augment_and_preprocess, num_parallel_calls=autotune).prefetch(autotune)
    valid_ds = valid_ds.map(preprocess_only, num_parallel_calls=autotune).prefetch(autotune)

    return train_ds, valid_ds, class_names


def build_model(num_classes: int, image_size: int) -> tf.keras.Model:
    """EfficientNetB0 transfer-learning model with a custom classification head.

    Inputs are expected to already be preprocessed via efficientnet.preprocess_input
    (done in the tf.data pipeline above / by PredictionService at inference), so no
    rescaling layer is included in the graph itself.
    """
    base_model = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(image_size, image_size, 3),
    )
    base_model.trainable = False  # Phase 1: feature extraction only

    inputs = tf.keras.Input(shape=(image_size, image_size, 3))
    # training=False keeps EfficientNet's BatchNorm layers in inference mode even
    # once the base is unfrozen for fine-tuning, preventing their running
    # statistics from being corrupted by small fine-tuning batches.
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs, name="plant_disease_efficientnetb0")
    model.base_model = base_model  # keep a handle for the fine-tuning phase
    return model


def get_callbacks(checkpoint_path: Path) -> list:
    return [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1),
        ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7, verbose=1),
    ]


def fine_tune(model: tf.keras.Model, unfreeze_layers: int, learning_rate: float) -> None:
    """Unfreezes the top N layers of the EfficientNetB0 base for fine-tuning."""
    base_model = model.base_model
    base_model.trainable = True

    for layer in base_model.layers[:-unfreeze_layers]:
        layer.trainable = False

    # Keep BatchNorm layers frozen even within the unfrozen range, so fine-tuning
    # doesn't destabilize normalization statistics learned on ImageNet.
    for layer in base_model.layers[-unfreeze_layers:]:
        if isinstance(layer, layers.BatchNormalization):
            layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    logger.info("Unfroze the top %d layers of EfficientNetB0 for fine-tuning", unfreeze_layers)


def evaluate_model(
    model: tf.keras.Model, valid_ds: tf.data.Dataset, class_names: List[str], output_dir: Path
) -> None:
    """Computes accuracy/precision/recall/F1 via a classification report and saves a confusion matrix plot."""
    y_true, y_pred = [], []
    for images, labels in valid_ds:
        predictions = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(predictions, axis=1))

    report = classification_report(y_true, y_pred, target_names=class_names, digits=4, zero_division=0)
    logger.info("Classification report:\n%s", report)
    (output_dir / "classification_report.txt").write_text(report, encoding="utf-8")

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(20, 18))
    sns.heatmap(cm, annot=False, cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix - Plant Disease Classification")
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    cm_path = output_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=150)
    plt.close()
    logger.info("Saved confusion matrix to %s", cm_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the plant disease detection model.")
    parser.add_argument("--dataset-dir", type=str, default=str(SCRIPT_DIR / "dataset"))
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_SAVED_MODEL_DIR))
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=15, help="Epochs for the frozen-base training phase.")
    parser.add_argument("--fine-tune-epochs", type=int, default=10, help="Epochs for the fine-tuning phase.")
    parser.add_argument(
        "--unfreeze-layers", type=int, default=40, help="Number of top EfficientNetB0 layers to unfreeze."
    )
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--fine-tune-learning-rate", type=float, default=1e-5)
    args = parser.parse_args()

    dataset_dir = Path(args.dataset_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / "plant_disease_model.keras"

    train_ds, valid_ds, class_names = build_datasets(dataset_dir, args.image_size, args.batch_size)

    # Overwrite class_names.json with the order actually discovered from disk, so the
    # backend's class index -> label mapping is always in sync with this trained model.
    with open(output_dir / "class_names.json", "w", encoding="utf-8") as file:
        json.dump(class_names, file, indent=2)
    logger.info("Saved class_names.json with %d classes", len(class_names))

    model = build_model(num_classes=len(class_names), image_size=args.image_size)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary(print_fn=logger.info)

    logger.info("Phase 1: training the classification head with a frozen EfficientNetB0 base")
    model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=args.epochs,
        callbacks=get_callbacks(checkpoint_path),
    )

    logger.info("Phase 2: fine-tuning the top layers of EfficientNetB0")
    fine_tune(model, unfreeze_layers=args.unfreeze_layers, learning_rate=args.fine_tune_learning_rate)
    model.fit(
        train_ds,
        validation_data=valid_ds,
        epochs=args.fine_tune_epochs,
        callbacks=get_callbacks(checkpoint_path),
    )

    # ModelCheckpoint already persisted the best-val-accuracy weights during both
    # phases; save once more to guarantee the artifact reflects the final state.
    model.save(checkpoint_path)
    logger.info("Saved final model to %s", checkpoint_path)

    evaluate_model(model, valid_ds, class_names, output_dir)


if __name__ == "__main__":
    main()
