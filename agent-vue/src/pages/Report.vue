<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useMessage, NButton, NCard, NSpin, NResult, NTag } from 'naive-ui'
import { useResumeStore } from '@/store/resume'
import ReportViewer from '@/components/ReportViewer.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const message = useMessage()
const resumeStore = useResumeStore()

const { loading } = storeToRefs(resumeStore)
const reportData = ref(null)
const localError = ref('')
const similarityPercent = computed(() =>
  typeof reportData.value?.similarity_score === 'number'
    ? Math.round(reportData.value.similarity_score * 100)
    : null
)

const encodedResume = computed(() => route.params.resume || '')
const jobId = computed(() => route.params.job || '')

function decodeParam(param) {
  try {
    return decodeURIComponent(param)
  } catch (error) {
    return param
  }
}

async function ensureResume() {
  if (resumeStore.resumeFile) {
    return true
  }
  const resumeParam = decodeParam(encodedResume.value)
  if (resumeParam) {
    resumeStore.setResume({ json_file: resumeParam })
    return true
  }
  message.warning(t('upload.errors.noData'))
  router.push({ name: 'upload' })
  return false
}

async function loadReport() {
  localError.value = ''
  reportData.value = null
  const ok = await ensureResume()
  if (!ok) return
  const id = decodeParam(jobId.value)
  if (!id) {
    message.warning(t('recommend.viewDetail'))
    router.push({ name: 'recommend' })
    return
  }
  try {
    const data = await resumeStore.fetchReport(id)
    reportData.value = data
  } catch (error) {
    localError.value = error.message || t('report.fetchFailed')
    message.error(localError.value)
  }
}

onMounted(() => {
  loadReport()
})

watch(
  () => route.params.job,
  () => {
    loadReport()
  }
)

function goBack() {
  router.push({ name: 'recommend' })
}

function refreshReport() {
  resumeStore.reportCache.delete(decodeParam(jobId.value))
  loadReport()
}
</script>

<template>
  <section class="report-page">
    <header class="page-header">
      <div>
        <h1>{{ t('report.pageTitle') }}</h1>
        <p v-if="reportData?.job_title">
          {{ reportData.job_title }} · {{ reportData.company }}
        </p>
      </div>
      <n-button quaternary size="medium" @click="goBack">
        {{ t('report.backToRecommend') }}
      </n-button>
    </header>

    <n-spin :show="loading.report">
      <template v-if="reportData">
        <n-card class="meta-card" size="large">
          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-label">{{ t('report.jobTitle') }}</span>
              <p class="meta-value">{{ reportData.job_title || '—' }}</p>
            </div>
            <div class="meta-item">
              <span class="meta-label">{{ t('report.company') }}</span>
              <p class="meta-value">{{ reportData.company || '—' }}</p>
            </div>
            <div class="meta-item">
              <span class="meta-label">{{ t('report.location') }}</span>
              <p class="meta-value">{{ reportData.location || '—' }}</p>
            </div>
            <div class="meta-item">
              <span class="meta-label">{{ t('report.resumeName') }}</span>
              <p class="meta-value">{{ reportData.resume_name || '—' }}</p>
            </div>
            <div class="meta-item highlight">
              <span class="meta-label">{{ t('report.similarityScore') }}</span>
              <n-tag type="success" round size="large" v-if="similarityPercent !== null">
                {{ similarityPercent }}%
              </n-tag>
              <p v-else class="meta-value">—</p>
            </div>
          </div>
        </n-card>

        <n-card class="report-card" size="large">
          <report-viewer
            :report-path="reportData.report_path"
            :analysis="reportData.analysis"
            :similarity-score="reportData.similarity_score"
            @refresh="refreshReport"
          />
        </n-card>
      </template>

      <n-result
        v-else
        status="info"
        :title="localError ? t('report.fetchFailed') : t('recommend.emptyTitle')"
        :description="localError || t('report.noContent')"
      >
        <template #footer>
          <n-button type="primary" @click="goBack">
            {{ t('common.back') }}
          </n-button>
        </template>
      </n-result>
    </n-spin>
  </section>
</template>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
  color: #1e293b;
}

.page-header p {
  margin: 6px 0 0;
  color: #64748b;
}

.report-card {
  border-radius: 18px;
  border: 1px solid #e2e8f0;
}

.meta-card {
  border-radius: 18px;
  border: 1px solid rgba(37, 99, 235, 0.18);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(56, 189, 248, 0.02));
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 18px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta-item.highlight {
  align-items: flex-start;
  justify-content: center;
}

.meta-label {
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #2563eb;
}

.meta-value {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}
</style>
