import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
})

export async function predictDisease(file, onUploadProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress,
  })
  return response.data
}

export async function fetchHistory(limit = 20, skip = 0) {
  const response = await apiClient.get('/history', { params: { limit, skip } })
  return response.data
}

export function extractErrorMessage(error) {
  if (error.response?.data?.message) return error.response.data.message
  if (error.code === 'ECONNABORTED') return 'The request timed out. Please try again.'
  if (error.message === 'Network Error') {
    return 'Cannot reach the server. Please make sure the backend is running.'
  }
  return 'Something went wrong while analyzing your image. Please try again.'
}
