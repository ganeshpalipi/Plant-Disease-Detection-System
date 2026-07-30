import ConfidenceBar from './ConfidenceBar.jsx'

function ResultCard({ result, imagePreviewUrl }) {
  const { plant, disease, confidence, is_healthy: isHealthy } = result

  return (
    <div className="animate-slide-up rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-6 sm:flex-row">
        {imagePreviewUrl && (
          <img
            src={imagePreviewUrl}
            alt="Analyzed leaf"
            className="h-48 w-full rounded-xl object-cover sm:h-40 sm:w-40"
          />
        )}

        <div className="flex-1">
          <span
            className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${
              isHealthy ? 'bg-primary-100 text-primary-700' : 'bg-red-100 text-red-700'
            }`}
          >
            {isHealthy ? 'Healthy' : 'Disease Detected'}
          </span>

          <h2 className="mt-3 text-2xl font-bold text-gray-900">
            {plant} — {disease}
          </h2>

          <div className="mt-4">
            <ConfidenceBar confidence={confidence} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResultCard
