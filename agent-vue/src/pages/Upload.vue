<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  NCard,
  NButton,
  NSpace,
  NDivider,
  NList,
  NListItem,
  NTag,
  NEmpty,
} from 'naive-ui'
import ResumeUpload from '@/components/ResumeUpload.vue'
import { useResumeStore } from '@/store/resume'

const { t } = useI18n()
const router = useRouter()
const resumeStore = useResumeStore()
const { resumePayload, loading } = storeToRefs(resumeStore)

const resumeData = computed(() => resumePayload.value?.resume_data || null)
const basicInfo = computed(() => resumeData.value?.basic_info || {})
const skills = computed(() => resumeData.value?.skills || [])
const experiences = computed(() => resumeData.value?.experience || [])

function handleUploaded() {
  // no-op: store already updated; computed values react
}

function viewRecommendations() {
  router.push({ name: 'recommend' })
}
</script>

<template>
  <section class="upload-page">
    <header class="page-header">
      <div>
        <h1>{{ t('upload.pageTitle') }}</h1>
        <p>{{ t('upload.instructions') }}</p>
      </div>
      <n-button
        v-if="resumeData"
        type="primary"
        size="large"
        :loading="loading.recommendations"
        @click="viewRecommendations"
      >
        {{ t('nav.recommend') }}
      </n-button>
    </header>

    <resume-upload @uploaded="handleUploaded" />

    <n-card v-if="resumeData" class="preview-card" size="large">
      <template #header>
        <div class="preview-header">
          <h2>{{ t('upload.previewTitle') }}</h2>
          <span v-if="resumePayload?.filename" class="file-name">
            {{ resumePayload.filename }}
          </span>
        </div>
      </template>

      <section class="preview-section">
        <h3>{{ t('upload.basicInfo') }}</h3>
        <n-list>
          <n-list-item v-if="basicInfo.name">
            <strong>{{ t('upload.basicInfo') }}</strong>：{{ basicInfo.name }}
          </n-list-item>
          <n-list-item v-if="basicInfo.email">
            <strong>Email</strong>：{{ basicInfo.email }}
          </n-list-item>
          <n-list-item v-if="basicInfo.phone">
            <strong>Phone</strong>：{{ basicInfo.phone }}
          </n-list-item>
        </n-list>
      </section>

      <n-divider />

      <section class="preview-section">
        <h3>{{ t('upload.skills') }}</h3>
        <div v-if="skills.length" class="skill-tags">
          <n-tag v-for="skill in skills" :key="skill" type="info" size="small">
            {{ skill }}
          </n-tag>
        </div>
        <n-empty v-else size="small" description="-" />
      </section>

      <n-divider />

      <section class="preview-section">
        <h3>{{ t('upload.experience') }}</h3>
        <n-list v-if="experiences.length">
          <n-list-item v-for="(exp, index) in experiences" :key="index">
            <article class="experience-item">
              <h4>{{ exp.company }} · {{ exp.role }}</h4>
              <p v-if="exp.duration">{{ exp.duration }}</p>
              <p v-if="exp.description">{{ exp.description }}</p>
            </article>
          </n-list-item>
        </n-list>
        <n-empty v-else size="small" :description="t('upload.errors.noData')" />
      </section>
    </n-card>
  </section>
</template>

<style scoped>
.upload-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 960px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.page-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
  color: #1e293b;
}

.page-header p {
  margin: 8px 0 0;
  color: #475569;
}

.preview-card {
  border-radius: 18px;
  border: 1px solid #e2e8f0;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.file-name {
  font-size: 14px;
  color: #64748b;
}

.preview-section {
  margin-bottom: 16px;
}

.preview-section h3 {
  margin: 0 0 12px;
  font-size: 18px;
  color: #1e293b;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.experience-item h4 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.experience-item p {
  margin: 0 0 4px;
  color: #64748b;
  line-height: 1.6;
}
</style>
