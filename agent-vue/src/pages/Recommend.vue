<script setup>
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useMessage, NSpin, NResult, NButton } from 'naive-ui'
import { useResumeStore } from '@/store/resume'
import MatchSummary from '@/components/MatchSummary.vue'
import JobCard from '@/components/JobCard.vue'

const { t } = useI18n()
const router = useRouter()
const message = useMessage()
const resumeStore = useResumeStore()

const { recommendations, recommendationSummary, loading, resumePayload, error } =
  storeToRefs(resumeStore)

async function loadRecommendations() {
  if (!resumeStore.resumeFile) return
  try {
    await resumeStore.fetchRecommendations()
  } catch (err) {
    if (err?.status === 404) {
      message.error(t('recommend.emptyDescription'))
    } else if (err?.status) {
      message.error(`${t('recommend.pageTitle')}: ${err.message}`)
    } else {
      message.error(err?.message || t('common.retry'))
    }
  }
}

function handleView(job) {
  router.push({
    name: 'report',
    params: {
      resume: encodeURIComponent(resumeStore.resumeFile),
      job: encodeURIComponent(job.job_id),
    },
  })
}

function goUpload() {
  router.push({ name: 'upload' })
}

onMounted(() => {
  if (!resumeStore.resumeFile) {
    message.warning(t('upload.errors.noData'))
    router.push({ name: 'upload' })
    return
  }
  if (!recommendations.value.length) {
    loadRecommendations()
  }
})

watch(
  () => error.value,
  (err) => {
    if (err) {
      message.error(err.message || t('common.retry'))
    }
  }
)
</script>

<template>
  <section class="recommend-page">
    <header class="page-header">
      <div>
        <h1>{{ t('recommend.pageTitle') }}</h1>
        <p v-if="resumePayload?.resume_data?.basic_info?.name">
          {{ resumePayload.resume_data.basic_info.name }}
        </p>
      </div>
      <n-button quaternary size="medium" @click="goUpload">
        {{ t('nav.upload') }}
      </n-button>
    </header>

    <n-spin :show="loading.recommendations">
      <div class="content">
        <match-summary
          v-if="recommendations.length"
          :summary="recommendationSummary"
          :total="recommendations.length"
          :top-score="recommendations[0]?.score ?? null"
        />

        <div v-if="recommendations.length" class="jobs-grid">
          <job-card
            v-for="job in recommendations"
            :key="job.job_id"
            :job="job"
            @view="handleView"
          />
        </div>

        <n-result
          v-else
          status="info"
          :title="t('recommend.emptyTitle')"
          :description="t('recommend.emptyDescription')"
        >
          <template #footer>
            <n-button type="primary" @click="goUpload">
              {{ t('home.cta') }}
            </n-button>
          </template>
        </n-result>
      </div>
    </n-spin>
  </section>
</template>

<style scoped>
.recommend-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1080px;
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
  margin: 4px 0 0;
  color: #64748b;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}
</style>
