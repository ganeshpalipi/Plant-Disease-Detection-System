const TECH_STACK = {
  'AI / Deep Learning': ['TensorFlow 2.x', 'EfficientNetB0 (Transfer Learning)', 'scikit-learn'],
  Backend: ['FastAPI', 'Python', 'OpenCV', 'Pillow', 'Pydantic', 'MongoDB'],
  Frontend: ['React.js', 'Vite', 'Tailwind CSS', 'Axios', 'React Router'],
}

const PIPELINE = [
  'User uploads a leaf image via the React frontend',
  'FastAPI validates the file (format, size, corruption checks)',
  'Image is preprocessed to 224×224 and normalized for EfficientNetB0',
  'The trained model predicts the plant and disease class',
  'A recommendation engine attaches description, symptoms, causes, treatment and prevention',
  'The prediction is logged to MongoDB and returned to the frontend as JSON',
]

function About() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
      <h1 className="text-3xl font-bold text-gray-900">About This Project</h1>
      <p className="mt-4 leading-relaxed text-gray-600">
        The Plant Disease Detection System is a deep learning-powered web application that identifies plant
        diseases from leaf images and — unlike a simple classifier — returns full, actionable guidance:
        a description of the disease, its symptoms, causes, recommended treatment, and prevention tips.
        It was built as a B.Tech CSE (AI &amp; ML) minor project, covering the full stack from model
        training to a production-style deployable web application.
      </p>

      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-900">Model Details</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          {[
            ['Architecture', 'EfficientNetB0 (Transfer Learning + Fine-Tuning)'],
            ['Dataset', 'PlantVillage — 38 classes, 14 plant species'],
            ['Input Size', '224 × 224 RGB'],
            ['Framework', 'TensorFlow 2.x / Keras'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-gray-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">{label}</p>
              <p className="mt-1 font-medium text-gray-800">{value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-900">How a Prediction Is Made</h2>
        <ol className="mt-4 space-y-3">
          {PIPELINE.map((step, index) => (
            <li key={step} className="flex gap-3">
              <span className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-700">
                {index + 1}
              </span>
              <span className="text-gray-600">{step}</span>
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold text-gray-900">Technology Stack</h2>
        <div className="mt-4 grid gap-6 sm:grid-cols-3">
          {Object.entries(TECH_STACK).map(([category, items]) => (
            <div key={category}>
              <h3 className="font-semibold text-gray-800">{category}</h3>
              <ul className="mt-2 space-y-1 text-sm text-gray-600">
                {items.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default About
