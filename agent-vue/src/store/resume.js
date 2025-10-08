import { defineStore } from 'pinia'
import { uploadResume } from '@/api/upload'
import { getMatchReport, getRecommendations } from '@/api/match'

export const useResumeStore = defineStore('resume', {
  state: () => ({
    resumePayload: null,
    recommendations: [],
    recommendationSummary: '',
    reportCache: new Map(),
    loading: {
      upload: false,
      recommendations: false,
      report: false,
    },
    error: null,
  }),
  getters: {
    hasResume(state) {
      return !!state.resumePayload
    },
    resumeFile(state) {
      const path = state.resumePayload?.json_file || ''
      if (!path) return ''
      const segments = path.split(/[/\\]/)
      return segments[segments.length - 1] || path
    },
  },
  actions: {
    setResume(payload) {
      if (!payload) return
      this.resumePayload = {
        ...(this.resumePayload || {}),
        ...payload,
      }
    },
    setRecommendations(list) {
      this.recommendations = list
    },
    clearError() {
      this.error = null
    },
    async upload(file) {
      this.loading.upload = true
      this.clearError()
      try {
        const response = await uploadResume(file)
        this.setResume(response.data)
        return this.resumePayload
      } catch (error) {
        this.error = error
        throw error
      } finally {
        this.loading.upload = false
      }
    },
    async fetchRecommendations(topK) {
      if (!this.resumeFile) {
        const error = new Error('RESUME_NOT_AVAILABLE')
        this.error = error
        throw error
      }
      this.loading.recommendations = true
      this.clearError()
      try {
        const { data } = await getRecommendations(this.resumeFile, topK)
        this.recommendations = data.recommendations || []
        this.recommendationSummary = data.summary || ''
        return data
      } catch (error) {
        this.recommendations = []
        this.recommendationSummary = ''
        this.error = error
        throw error
      } finally {
        this.loading.recommendations = false
      }
    },
    async fetchReport(jobId) {
      if (!this.resumeFile) {
        const error = new Error('RESUME_NOT_AVAILABLE')
        this.error = error
        throw error
      }
      if (!jobId) {
        const error = new Error('MISSING_JOB_ID')
        this.error = error
        throw error
      }
      if (this.reportCache.has(jobId)) {
        return this.reportCache.get(jobId)
      }
      this.loading.report = true
      this.clearError()
      try {
        const { data } = await getMatchReport(this.resumeFile, jobId)
        this.reportCache.set(jobId, data)
        return data
      } catch (error) {
        this.error = error
        throw error
      } finally {
        this.loading.report = false
      }
    },
    reset() {
      this.resumePayload = null
      this.recommendations = []
      this.recommendationSummary = ''
      this.reportCache = new Map()
      this.loading = {
        upload: false,
        recommendations: false,
        report: false,
      }
      this.error = null
    },
  },
})
