<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMessage, NSpin, NAlert, NButton } from 'naive-ui'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({
  breaks: true,
  gfm: true,
})

const props = defineProps({
  reportPath: {
    type: String,
    required: true,
  },
  analysis: {
    type: String,
    default: '',
  },
  similarityScore: {
    type: Number,
    default: null,
  },
})

const emits = defineEmits(['refresh'])

const { t } = useI18n()
const message = useMessage()

const loading = ref(false)
const htmlContent = ref('')
const error = ref('')
const sections = computed(() => parseAnalysisSections(props.analysis))

async function fetchReport() {
  if (!props.reportPath) return
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(
      props.reportPath.startsWith('/') ? props.reportPath : `/${props.reportPath}`,
      {
        credentials: 'include',
      }
    )
    if (!response.ok) {
      throw new Error(`${response.status}`)
    }
    const raw = await response.text()
    const trimmed = raw.trim()
    const containsHtmlTag = /<\/?[a-z][^>]*>/i.test(trimmed)
    const parsed = containsHtmlTag ? trimmed : marked.parse(trimmed)
    htmlContent.value = DOMPurify.sanitize(parsed, {
      ADD_ATTR: ['target', 'style'],
    })
  } catch (err) {
    error.value = err?.message || t('report.fetchFailed')
    message.error(error.value)
  } finally {
    loading.value = false
  }
}

watch(
  () => props.reportPath,
  () => {
    fetchReport()
  },
  { immediate: true }
)

function handleRefresh() {
  emits('refresh')
  fetchReport()
}

function parseAnalysisSections(text) {
  if (!text) return []
  const lines = text
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map((line) => line.trim())

  const cards = []
  let current = null

  const pushItem = (item) => {
    if (!item) return
    if (!current) return
    const normalized = item
      .replace(/^\*\*/g, '')
      .replace(/\*\*$/g, '')
      .replace(/^[-•]\s*/, '')
      .trim()
    if (normalized) {
      current.items.push(normalized)
    }
  }

  for (const line of lines) {
    if (!line) continue
    const sectionMatch = line.match(/^\*\*(.+?)\*\*\s*[:：]\s*(.*)$/)
    if (sectionMatch) {
      const [, title, rest] = sectionMatch
      current = {
        title: title.trim(),
        items: [],
      }
      cards.push(current)
      pushItem(rest)
      continue
    }
    if (!current) continue
    if (/^[-•]/.test(line)) {
      pushItem(line)
    } else if (current.items.length > 0) {
      current.items[current.items.length - 1] += ` ${line}`
    } else {
      pushItem(line)
    }
  }

  return cards.filter((card) => card.items.length > 0)
}
</script>

<template>
  <section class="report-viewer">
    <header class="report-header">
      <h2>{{ t('report.analysisTitle') }}</h2>
      <div class="header-actions">
        <div v-if="similarityScore !== null" class="score-chip">
          {{ t('report.similarityScore') }}: {{ Math.round(similarityScore * 100) }}%
        </div>
        <n-button size="small" quaternary @click="handleRefresh">
          {{ t('report.refresh') }}
        </n-button>
      </div>
    </header>

    <p v-if="analysis" class="analysis-text">
      {{ analysis }}
    </p>

    <section v-if="sections.length" class="section-grid">
      <n-card
        v-for="card in sections"
        :key="card.title"
        class="section-card"
        size="small"
        :segmented="{ content: true }"
      >
        <template #header>
          <h3 class="section-title">{{ card.title }}</h3>
        </template>
        <ul class="section-list">
          <li v-for="(item, index) in card.items" :key="index">{{ item }}</li>
        </ul>
      </n-card>
    </section>

    <n-alert
      v-if="error"
      type="error"
      :title="t('report.fetchFailed')"
      class="report-alert"
    >
      {{ error }}
    </n-alert>

    <div class="report-content">
      <n-spin :show="loading">
        <div v-if="htmlContent" class="html-container" v-html="htmlContent" />
        <p v-else-if="!loading && !error" class="placeholder">
          {{ t('report.noContent') }}
        </p>
      </n-spin>
    </div>
  </section>
</template>

<style scoped>
.report-viewer {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.report-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1e293b;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
  font-weight: 600;
}

.analysis-text {
  margin: 0;
  color: #475569;
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.section-card {
  border-radius: 16px;
  border: 1px solid rgba(37, 99, 235, 0.16);
  background: linear-gradient(
    160deg,
    rgba(37, 99, 235, 0.08) 0%,
    rgba(248, 250, 252, 0.85) 100%
  );
}

.section-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1d4ed8;
}

.section-list {
  margin: 0;
  padding-left: 18px;
  color: #1e293b;
  line-height: 1.6;
}

.report-alert {
  border-radius: 12px;
}

.report-content {
  min-height: 360px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 28px;
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.06);
}

.html-container {
  font-family: "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI",
    "Helvetica Neue", Arial, sans-serif;
  color: #1e293b;
  line-height: 1.75;
  font-size: 15px;
}

.html-container :deep(h1),
.html-container :deep(h2),
.html-container :deep(h3),
.html-container :deep(h4) {
  color: #0f172a;
  font-weight: 700;
  margin-top: 28px;
  margin-bottom: 12px;
}

.html-container :deep(h1) {
  font-size: 28px;
  border-bottom: 2px solid rgba(37, 99, 235, 0.14);
  padding-bottom: 12px;
}

.html-container :deep(h2) {
  font-size: 22px;
}

.html-container :deep(h3) {
  font-size: 19px;
}

.html-container :deep(p) {
  margin: 12px 0;
}

.html-container :deep(ul),
.html-container :deep(ol) {
  padding-left: 22px;
  margin: 12px 0;
}

.html-container :deep(li) {
  margin: 6px 0;
}

.html-container :deep(strong) {
  color: #1d4ed8;
  font-weight: 600;
}

.html-container :deep(em) {
  color: #0f172a;
  font-style: italic;
}

.html-container :deep(blockquote) {
  margin: 16px 0;
  padding: 16px 18px;
  border-left: 4px solid #60a5fa;
  background: rgba(96, 165, 250, 0.12);
  border-radius: 12px;
  color: #1e293b;
}

.html-container :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.html-container :deep(th),
.html-container :deep(td) {
  border: 1px solid #e2e8f0;
  padding: 10px 12px;
  text-align: left;
}

.html-container :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.08);
  font-family: "Fira Code", "JetBrains Mono", Consolas, monospace;
  font-size: 0.92em;
}

.html-container :deep(pre) {
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.09);
  overflow-x: auto;
}

.placeholder {
  margin: 0;
  color: #94a3b8;
  text-align: center;
  padding: 48px 0;
}
</style>
