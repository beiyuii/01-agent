import axios from 'axios'

const REQUEST_TIMEOUT = Number.parseInt(
  import.meta.env.VITE_API_TIMEOUT ?? '60000',
  10
)

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
  timeout: Number.isFinite(REQUEST_TIMEOUT) ? REQUEST_TIMEOUT : 60000,
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const parsedError = {
      message: error.response?.data?.detail || error.message,
      status: error.response?.status,
      data: error.response?.data,
    }
    return Promise.reject(parsedError)
  }
)

export default instance
