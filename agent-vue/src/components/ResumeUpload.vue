<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMessage, NUpload, NUploadDragger, NButton, NAlert, NIcon } from 'naive-ui'
import { CloudUploadOutline } from '@vicons/ionicons5'
import { useResumeStore } from '@/store/resume'

const emits = defineEmits(['uploaded'])

const { t } = useI18n()
const message = useMessage()
const resumeStore = useResumeStore()

const fileList = ref([])
const errorMessage = ref('')
const successMessage = ref('')

const isUploading = computed(() => resumeStore.loading.upload)

const allowedTypes = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
]

function resetStatus() {
  errorMessage.value = ''
  successMessage.value = ''
}

function beforeUpload({ file }) {
  resetStatus()
  const raw = file.file
  if (!allowedTypes.includes(raw.type)) {
    errorMessage.value = t('upload.errors.unsupported')
    message.error(errorMessage.value)
    return false
  }
  if (raw.size / 1024 / 1024 > 10) {
    errorMessage.value = t('upload.errors.tooLarge')
    message.error(errorMessage.value)
    return false
  }
  fileList.value = [file]
  return true
}

async function customUpload({ file, onError, onFinish }) {
  resetStatus()
  try {
    const result = await resumeStore.upload(file.file)
    successMessage.value = t('upload.status.success')
    emits('uploaded', result)
    onFinish()
  } catch (error) {
    errorMessage.value = error?.message || t('upload.status.failed')
    onError(error)
  }
}

function handleChange({ fileList: list }) {
  fileList.value = list
}
</script>

<template>
  <div class="upload-card">
    <n-upload
      :file-list="fileList"
      :disabled="isUploading"
      :max="1"
      :show-file-list="false"
      :custom-request="customUpload"
      :on-before-upload="beforeUpload"
      @change="handleChange"
    >
      <n-upload-dragger class="upload-dragger">
        <div class="icon-wrapper">
          <n-icon size="36" :component="CloudUploadOutline" />
        </div>
        <div class="title">{{ t('upload.instructions') }}</div>
        <div class="subtitle">{{ t('upload.supportedTypes') }}</div>
        <n-button type="primary" size="small" quaternary style="margin-top: 12px">
          {{ isUploading ? t('upload.status.uploading') : t('upload.selectFile') }}
        </n-button>
      </n-upload-dragger>
    </n-upload>

    <transition name="fade">
      <n-alert
        v-if="successMessage"
        type="success"
        :title="t('upload.status.successTitle')"
        class="status-alert"
      >
        {{ successMessage }}
      </n-alert>
    </transition>
    <transition name="fade">
      <n-alert
        v-if="errorMessage"
        type="error"
        :title="t('upload.status.errorTitle')"
        class="status-alert"
      >
        {{ errorMessage }}
      </n-alert>
    </transition>
  </div>
</template>

<style scoped>
.upload-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-dragger {
  padding: 32px 24px;
  border-radius: 16px;
  border: 1px dashed #2563eb33;
  background: #ffffff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.upload-dragger:hover {
  border-color: #2563eb;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.08);
}

.icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(56, 189, 248, 0.12));
  color: #2563eb;
  margin: 0 auto 16px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: #64748b;
}

.status-alert {
  border-radius: 12px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
