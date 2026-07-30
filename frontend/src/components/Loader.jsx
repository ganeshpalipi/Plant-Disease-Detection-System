function Loader({ message = 'Loading...', progress }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12 text-center">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary-200 border-t-primary-600" />
      <p className="text-sm font-medium text-gray-600">{message}</p>
      {typeof progress === 'number' && progress > 0 && (
        <div className="h-2 w-48 overflow-hidden rounded-full bg-gray-200">
          <div
            className="h-full rounded-full bg-primary-600 transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}
    </div>
  )
}

export default Loader
