import { useNavigate } from 'react-router-dom'
import UploadCard from '../components/UploadCard.jsx'
import { usePrediction } from '../hooks/usePrediction.js'

function Upload() {
  const navigate = useNavigate()
  const { predict, isLoading, error, progress } = usePrediction()

  const handleAnalyze = async (file) => {
    try {
      const result = await predict(file)
      // A dedicated object URL for the Result page - independent of UploadCard's own
      // preview, which gets revoked as soon as this component unmounts on navigation.
      const imagePreviewUrl = URL.createObjectURL(file)
      navigate('/result', { state: { result, imagePreviewUrl } })
    } catch {
      // Error state is already surfaced via the `error` value from usePrediction.
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
      <h1 className="text-center text-3xl font-bold text-gray-900">Upload a Leaf Image</h1>
      <p className="mt-2 text-center text-gray-600">
        For best results, use a clear, well-lit photo of a single leaf against a plain background.
      </p>

      <div className="mt-8">
        <UploadCard onAnalyze={handleAnalyze} isLoading={isLoading} progress={progress} />
      </div>

      {error && !isLoading && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          {error}
        </div>
      )}
    </div>
  )
}

export default Upload
