import { useEffect } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import ResultCard from '../components/ResultCard.jsx'
import DiseaseInfoAccordion from '../components/DiseaseInfoAccordion.jsx'

function Result() {
  const location = useLocation()
  const { result, imagePreviewUrl } = location.state ?? {}

  useEffect(() => {
    return () => {
      if (imagePreviewUrl) URL.revokeObjectURL(imagePreviewUrl)
    }
  }, [imagePreviewUrl])

  if (!result) {
    return <Navigate to="/upload" replace />
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <h1 className="text-center text-3xl font-bold text-gray-900">Diagnosis Result</h1>

      <div className="mt-8">
        <ResultCard result={result} imagePreviewUrl={imagePreviewUrl} />
        <DiseaseInfoAccordion result={result} />
      </div>

      <div className="mt-8 text-center">
        <Link
          to="/upload"
          className="inline-block rounded-xl bg-primary-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-primary-700"
        >
          Analyze Another Image
        </Link>
      </div>
    </div>
  )
}

export default Result
