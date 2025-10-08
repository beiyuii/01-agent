import api from './axiosInstance'

export function getRecommendations(resumeFile, topK) {
  if (!resumeFile) {
    return Promise.reject(new Error('MISSING_RESUME_FILE'))
  }

  return api.get('/match/auto', {
    params: {
      resume_file: resumeFile,
      ...(topK ? { top_k: topK } : {}),
    },
  })
}

export function getMatchReport(resumeFile, jobId) {
  if (!resumeFile || !jobId) {
    return Promise.reject(new Error('MISSING_REPORT_PARAMS'))
  }

  return api.get('/match/single', {
    params: {
      resume_file: resumeFile,
      job_id: jobId,
    },
  })
}
