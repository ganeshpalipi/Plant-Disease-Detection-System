function getColor(confidence) {
  if (confidence >= 80) return 'bg-primary-600'
  if (confidence >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

function ConfidenceBar({ confidence }) {
  const clamped = Math.min(100, Math.max(0, confidence))

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-sm font-medium text-gray-600">
        <span>Confidence</span>
        <span>{clamped.toFixed(2)}%</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full transition-all duration-700 ${getColor(clamped)}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  )
}

export default ConfidenceBar
