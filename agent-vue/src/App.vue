<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  NConfigProvider,
  NGlobalStyle,
  NMessageProvider,
  NLayout,
  NLayoutHeader,
  NLayoutContent,
  NLayoutFooter,
} from 'naive-ui'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const { t } = useI18n()
const currentYear = new Date().getFullYear()

const themeOverrides = ref({
  common: {
    fontFamily:
      '"Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif',
    primaryColor: '#2563EB',
    primaryColorHover: '#1D4ED8',
    primaryColorPressed: '#1D4ED8',
    primaryColorSuppl: '#60A5FA',
    infoColor: '#38BDF8',
    infoColorHover: '#0EA5E9',
    infoColorPressed: '#0284C7',
    infoColorSuppl: '#38BDF8',
    successColor: '#10B981',
    successColorHover: '#059669',
    errorColor: '#F43F5E',
    errorColorHover: '#E11D48',
    textColorBase: '#1E293B',
    textColor2: '#64748B',
    borderColor: '#E2E8F0',
    borderRadius: '12px',
    borderRadiusMedium: '14px',
    bodyColor: '#F8FAFC',
    cardColor: '#FFFFFF',
  },
})

const navLinks = computed(() => [
  { name: 'home', label: t('nav.home'), to: { name: 'home' } },
  { name: 'upload', label: t('nav.upload'), to: { name: 'upload' } },
  { name: 'recommend', label: t('nav.recommend'), to: { name: 'recommend' } },
])
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-global-style />
    <n-message-provider>
      <div class="app-shell">
        <n-layout class="app-layout">
          <n-layout-header bordered class="app-header">
            <div class="brand">
              <span class="brand-mark">AI</span>
              <span class="brand-name">{{ t('app.title') }}</span>
            </div>
            <nav class="nav-links">
              <RouterLink
                v-for="link in navLinks"
                :key="link.name"
                :to="link.to"
                class="nav-link"
                active-class="active"
              >
                {{ link.label }}
              </RouterLink>
            </nav>
            <LanguageSwitcher />
          </n-layout-header>
          <n-layout-content class="app-content" content-style="max-width: 1080px; margin: 0 auto;">
            <RouterView />
          </n-layout-content>
          <n-layout-footer class="app-footer">
            {{ t('common.footer', { year: currentYear }) }}
          </n-layout-footer>
        </n-layout>
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: transparent;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: #f8fafc;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 18px;
  color: #1e293b;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%);
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 1px;
}

.nav-links {
  display: flex;
  gap: 16px;
}

.nav-link {
  padding: 6px 12px;
  border-radius: 8px;
  font-weight: 500;
  color: #64748b;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.nav-link:hover {
  color: #1d4ed8;
  background-color: rgba(37, 99, 235, 0.08);
}

.nav-link.active {
  color: #2563eb;
  background-color: rgba(37, 99, 235, 0.12);
}

.app-footer {
  background-color: #f8fafc;
}
</style>
