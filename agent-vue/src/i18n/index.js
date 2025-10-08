import { watch } from 'vue'
import { createI18n } from 'vue-i18n'
import en from './en.json'
import zh from './zh.json'

const fallbackLocale = 'zh'
const storedLocale =
  typeof window !== 'undefined' ? localStorage.getItem('locale') : null

const i18n = createI18n({
  legacy: false,
  locale: storedLocale || fallbackLocale,
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
  },
})

if (typeof window !== 'undefined') {
  watch(
    () => i18n.global.locale.value,
    (locale) => {
      localStorage.setItem('locale', locale)
    },
    { immediate: true }
  )
}

export default i18n
