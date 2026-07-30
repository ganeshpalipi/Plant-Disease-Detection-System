import { useCallback, useEffect, useRef, useState } from 'react'

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png']
const MAX_SIZE_MB = 10

function UploadCard({ onAnalyze, isLoading, progress = 0 }) {
  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [validationError, setValidationError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleFile = useCallback((selected) => {
    setValidationError(null)
    if (!selected) return

    if (!ACCEPTED_TYPES.includes(selected.type)) {
      setValidationError('Please upload a JPG or PNG image.')
      return
    }
    if (selected.size > MAX_SIZE_MB * 1024 * 1024) {
      setValidationError(`Image must be smaller than ${MAX_SIZE_MB}MB.`)
      return
    }

    setFile(selected)
    setPreviewUrl(URL.createObjectURL(selected))
  }, [])

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault()
      setIsDragging(false)
      handleFile(event.dataTransfer.files?.[0])
    },
    [handleFile],
  )

  const handleClear = () => {
    setFile(null)
    setPreviewUrl(null)
    setValidationError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleSubmit = (event) => {
    event.preventDefault()
    if (file) onAnalyze(file)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
          isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-white hover:border-primary-400'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          className="hidden"
          onChange={(event) => handleFile(event.target.files?.[0])}
        />

        {previewUrl ? (
          <img src={previewUrl} alt="Selected leaf preview" className="max-h-64 rounded-xl object-contain" />
        ) : (
          <>
            <span className="mb-3 text-4xl" aria-hidden="true">
              📷
            </span>
            <p className="font-medium text-gray-700">Drag &amp; drop a leaf image here</p>
            <p className="mt-1 text-sm text-gray-500">
              or click to browse (JPG, JPEG, PNG — up to {MAX_SIZE_MB}MB)
            </p>
          </>
        )}
      </div>

      {validationError && <p className="mt-3 text-sm font-medium text-red-600">{validationError}</p>}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="submit"
          disabled={!file || isLoading}
          className="flex-1 rounded-xl bg-primary-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Leaf'}
        </button>
        {file && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="rounded-xl border border-gray-300 px-6 py-3 font-semibold text-gray-600 transition-colors hover:bg-gray-50"
          >
            Clear
          </button>
        )}
      </div>

      {isLoading && progress > 0 && (
        <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-primary-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </form>
  )
}

export default UploadCard
