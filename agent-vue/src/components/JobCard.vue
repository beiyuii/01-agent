<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NSpace, NButton, NTag, NStatistic } from 'naive-ui'

const props = defineProps({
  job: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits(['view'])

const { t, locale } = useI18n()

const formattedScore = computed(() => {
  if (typeof props.job.score === 'number') {
    return Math.round(props.job.score * 100)
  }
  return null
})

const deadlineLabel = computed(() => {
  const { deadline } = props.job
  if (!deadline) return ''
  try {
    const date = new Date(deadline)
    if (Number.isNaN(date.getTime())) return deadline
    return date.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch (error) {
    return deadline
  }
})

function handleView() {
  emits('view', props.job)
}
</script>

<template>
  <n-card class="job-card" size="large">
    <div class="job-card__header">
      <div>
        <h3 class="job-title">{{ job.title }}</h3>
        <div class="job-meta">
          <span>{{ job.company }}</span>
          <span v-if="job.location">· {{ job.location }}</span>
        </div>
      </div>
      <div v-if="formattedScore !== null" class="score-box">
        <n-statistic
          :label="t('recommend.matchScore')"
          :value="formattedScore"
          suffix="%"
        />
      </div>
    </div>

    <p v-if="job.snippet" class="job-snippet">
      {{ job.snippet }}
    </p>

    <n-space justify="space-between" align="center">
      <div class="tags">
        <n-tag v-if="job.deadline" type="info" size="small" class="tag-chip">
          {{ t('recommend.deadline') }}: {{ deadlineLabel }}
        </n-tag>
        <n-tag v-if="job.batch" size="small" class="tag-chip">
          {{ job.batch }}
        </n-tag>
        <n-tag v-if="job.industry" size="small" class="tag-chip">
          {{ job.industry }}
        </n-tag>
      </div>
      <n-button type="primary" size="small" @click="handleView">
        {{ t('recommend.viewDetail') }}
      </n-button>
    </n-space>
  </n-card>
</template>

<style scoped>
.job-card {
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
}

.job-card__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.job-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.job-meta {
  margin-top: 6px;
  color: #64748b;
  font-size: 14px;
}

.score-box {
  min-width: 120px;
  text-align: right;
}

.job-snippet {
  margin: 16px 0;
  color: #475569;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  border-radius: 10px;
}
</style>
