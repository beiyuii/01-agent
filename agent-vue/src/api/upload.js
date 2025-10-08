import api from './axiosInstance'

export function uploadResume(file) {
  if (!(file instanceof File)) {
    return Promise.reject(new Error('INVALID_FILE'))
  }

  const formData = new FormData()
  formData.append('file', file)

  return api.post('/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}
