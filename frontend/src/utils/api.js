import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 minutes for large PDFs
})

export async function uploadStatement(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) {
        onProgress(Math.round((evt.loaded / evt.total) * 40)) // upload = first 40%
      }
    },
  })

  return response.data
}

export function getDownloadUrl(sessionId) {
  return `${BASE_URL}/download/${sessionId}`
}
