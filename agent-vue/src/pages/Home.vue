<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { NButton, NCard, NSpace } from 'naive-ui'

const { t } = useI18n()
const router = useRouter()

function goToUpload() {
  router.push({ name: 'upload' })
}
</script>

<template>
  <section class="home-container">
    <header class="hero">
      <div class="hero-text">
        <h1>{{ t('home.headline') }}</h1>
        <p>{{ t('home.description') }}</p>
        <n-button type="primary" size="large" @click="goToUpload">
          {{ t('home.cta') }}
        </n-button>
      </div>
      <div class="hero-visual">
        <div class="visual-card">
          <span class="glow" />
          <div class="visual-content">
            <h3>AI</h3>
            <p>Resume Insight</p>
          </div>
        </div>
      </div>
    </header>

    <section class="steps-section">
      <h2>{{ t('home.stepsTitle') }}</h2>
      <n-space size="large" class="steps-grid">
        <n-card class="step-card" size="large">
          <span class="step-index">01</span>
          <h3>{{ t('home.stepUpload') }}</h3>
        </n-card>
        <n-card class="step-card" size="large">
          <span class="step-index">02</span>
          <h3>{{ t('home.stepRecommend') }}</h3>
        </n-card>
        <n-card class="step-card" size="large">
          <span class="step-index">03</span>
          <h3>{{ t('home.stepReport') }}</h3>
        </n-card>
      </n-space>
    </section>
  </section>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.hero {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 32px;
  align-items: center;
}

.hero-text h1 {
  margin: 0;
  font-size: 42px;
  font-weight: 700;
  color: #1e293b;
}

.hero-text p {
  margin: 18px 0 28px;
  font-size: 16px;
  line-height: 1.7;
  color: #475569;
}

.hero-visual {
  display: flex;
  justify-content: center;
}

.visual-card {
  position: relative;
  width: 260px;
  height: 260px;
  border-radius: 32px;
  background: linear-gradient(180deg, rgba(37, 99, 235, 0.18) 0%, rgba(37, 99, 235, 0) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.glow {
  position: absolute;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, rgba(37, 99, 235, 0) 70%);
  animation: pulse 4s ease-in-out infinite;
}

.visual-content {
  position: relative;
  text-align: center;
  color: #1e293b;
}

.visual-content h3 {
  margin: 0;
  font-size: 56px;
  letter-spacing: 4px;
}

.visual-content p {
  margin: 8px 0 0;
  font-size: 16px;
  letter-spacing: 1px;
}

.steps-section h2 {
  margin: 0 0 24px;
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.step-card {
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
}

.step-index {
  font-size: 16px;
  font-weight: 600;
  color: #38bdf8;
}

.step-card h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
  line-height: 1.5;
}

@keyframes pulse {
  0% {
    transform: scale(0.9);
    opacity: 0.6;
  }
  50% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.9);
    opacity: 0.6;
  }
}

@media (max-width: 768px) {
  .hero-text h1 {
    font-size: 32px;
  }
}
</style>
