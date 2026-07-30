import { Link } from 'react-router-dom'

function NotFound() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center px-4 py-24 text-center sm:px-6">
      <span className="text-6xl" aria-hidden="true">
        🍂
      </span>
      <h1 className="mt-6 text-4xl font-extrabold text-gray-900">404</h1>
      <p className="mt-2 text-lg text-gray-600">This page seems to have wilted away.</p>
      <Link
        to="/"
        className="mt-8 rounded-xl bg-primary-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-primary-700"
      >
        Back to Home
      </Link>
    </div>
  )
}

export default NotFound
