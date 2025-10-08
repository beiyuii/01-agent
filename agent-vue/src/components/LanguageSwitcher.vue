<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { NSelect } from 'naive-ui'

const { locale } = useI18n({ useScope: 'global' })

const options = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' },
]

const value = computed({
  get: () => locale.value,
  set: (nextLocale) => {
    locale.value = nextLocale
  },
})
</script>

<template>
  <n-select
    v-model:value="value"
    :options="options"
    size="small"
    class="language-switcher"
    :style="{ width: '140px' }"
  />
</template>

<style scoped>
.language-switcher {
  --n-border-radius: 10px;
}
</style>
