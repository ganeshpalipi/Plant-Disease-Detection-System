import { useCallback, useState } from 'react'
import { extractErrorMessage, predictDisease } from '../services/api.js'

export function usePrediction() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState(0)

  const predict = useCallback(async (file) => {
    setIsLoading(true)
    setError(null)
    setProgress(0)
    try {
      const data = await predictDisease(file, (event) => {
        if (event.total) {
          setProgress(Math.round((event.loaded * 100) / event.total))
        }
      })
      return data
    } catch (err) {
      setError(extractErrorMessage(err))
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  return { predict, isLoading, error, progress, setError }
}
