<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NCard, NStatistic, NSpace } from 'naive-ui'

const props = defineProps({
  summary: {
    type: String,
    default: '',
  },
  total: {
    type: Number,
    default: 0,
  },
  topScore: {
    type: Number,
    default: null,
  },
})

const { t } = useI18n()

const formattedTopScore = computed(() => {
  if (typeof props.topScore === 'number') {
    return Math.round(props.topScore * 100)
  }
  return null
})
</script>

<template>
  <n-card class="summary-card" size="large" :segmented="{ content: true, footer: true }">
    <template #header>
      <h3 class="summary-title">{{ t('recommend.summaryTitle') }}</h3>
    </template>

    <p class="summary-text">
      {{ summary || t('recommend.summaryEmpty') }}
    </p>

    <template #footer>
      <n-space justify="space-between" class="summary-foot">
        <n-statistic :label="t('recommend.totalMatches')" :value="total" />
        <n-statistic
          v-if="formattedTopScore !== null"
          :label="t('recommend.bestMatchScore')"
          :value="formattedTopScore"
          suffix="%"
        />
      </n-space>
    </template>
  </n-card>
</template>

<style scoped>
.summary-card {
  border-radius: 16px;
  border: 1px solid #2563eb1a;
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.06) 0%, rgba(248, 250, 252, 0) 100%);
}

.summary-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.summary-text {
  margin: 0;
  line-height: 1.6;
  color: #475569;
}

.summary-foot {
  width: 100%;
}
</style>
