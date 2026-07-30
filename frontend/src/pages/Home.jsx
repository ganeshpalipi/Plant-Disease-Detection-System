import { Link } from 'react-router-dom'

const STEPS = [
  { icon: '📤', title: 'Upload a Leaf Photo', description: 'Take or upload a clear photo of a plant leaf.' },
  { icon: '🧠', title: 'AI Analyzes the Image', description: 'EfficientNetB0 classifies the leaf across 38 disease classes.' },
  {
    icon: '📋',
    title: 'Get Actionable Results',
    description: 'Receive the disease name, confidence score, and full treatment guidance.',
  },
]

const PLANTS = [
  'Apple', 'Blueberry', 'Cherry', 'Corn', 'Grape', 'Orange', 'Peach',
  'Pepper Bell', 'Potato', 'Raspberry', 'Soybean', 'Squash', 'Strawberry', 'Tomato',
]

const FEATURES = [
  { icon: '⚡', title: 'Instant Diagnosis', description: 'Get results in seconds powered by deep learning.' },
  { icon: '🎯', title: '38 Disease Classes', description: 'Trained on the full PlantVillage dataset across 14 plant species.' },
  { icon: '📖', title: 'Full Recommendations', description: 'Symptoms, causes, treatment and prevention — not just a label.' },
]

function Home() {
  return (
    <div>
      <section className="bg-gradient-to-b from-primary-50 to-white">
        <div className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6">
          <span className="inline-block rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700">
            Deep Learning · EfficientNetB0 · 38 Plant Diseases
          </span>
          <h1 className="mt-6 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">
            Diagnose Plant Diseases Instantly with AI
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Upload a photo of a leaf and get an instant diagnosis — plant name, disease, confidence score,
            and complete treatment recommendations.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              to="/upload"
              className="rounded-xl bg-primary-600 px-8 py-3 font-semibold text-white shadow-sm transition-colors hover:bg-primary-700"
            >
              Analyze a Leaf Now
            </Link>
            <Link
              to="/about"
              className="rounded-xl border border-gray-300 bg-white px-8 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            >
              Learn How It Works
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-bold text-gray-900">How It Works</h2>
        <div className="mt-10 grid gap-8 sm:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.title} className="rounded-2xl border border-gray-200 bg-white p-6 text-center shadow-sm">
              <span className="text-4xl">{step.icon}</span>
              <h3 className="mt-4 font-semibold text-gray-900">{step.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <h2 className="text-center text-2xl font-bold text-gray-900">Why This Tool</h2>
          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            {FEATURES.map((feature) => (
              <div key={feature.title} className="text-center">
                <span className="text-3xl">{feature.icon}</span>
                <h3 className="mt-3 font-semibold text-gray-900">{feature.title}</h3>
                <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <h2 className="text-center text-2xl font-bold text-gray-900">Supported Plants</h2>
        <p className="mx-auto mt-2 max-w-xl text-center text-gray-600">
          Trained across 14 plant species covering all 38 classes of the PlantVillage dataset.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          {PLANTS.map((plant) => (
            <span
              key={plant}
              className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm"
            >
              {plant}
            </span>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home
