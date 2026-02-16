<script setup lang="ts">
import { ref, watch } from 'vue'
import { useAsyncTask } from 'vue-concurrency'

import { API } from '@/api'
import Divider from '@/components/DividerItem.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import Response from '@/components/ResponseItem.vue'
import { useStatus } from '@/composables/useStatus'
import type { ResponseType } from '@/schemas'

const file = ref<File>()
const filename = ref<string>()
const dragDropFocus = ref(false)
const { status } = useStatus()

const analyzeTask = useAsyncTask<ResponseType, [File]>(async (_signal, file: File) => {
  return await API.analyze(file)
})

const updateDragDropFocus = (value: boolean) => {
  dragDropFocus.value = value
}

const analyze = async () => {
  if (file.value) {
    await analyzeTask.perform(file.value)
  }
}

const onFileChangeDrop = (event: DragEvent) => {
  dragDropFocus.value = false
  if (event?.dataTransfer?.files) {
    file.value = event.dataTransfer.files[0]
  }
}

const onFileChange = (event: Event) => {
  const f = (event.target as HTMLInputElement).files?.[0]
  if (f) {
    file.value = f
  }
}

watch(file, () => {
  if (file.value) {
    filename.value = file.value.name
  }
})
</script>

<template>
  <div class="grid gap-4">
    <div class="alert border-info">
      <font-awesome-icon icon="info-circle" class="w-6 h-6 mr-2" />
      <ul class="list-disc list-inside space-y-1">
        <li>EML (<b>.eml</b>) and MSG (<b>.msg</b>) formats are supported.</li>
        <li>
          The MSG file will be converted to the EML file before analyzing. The conversion might be
          lossy.
        </li>
        <li v-if="!status.cache">This app doesn't store EML/MSG file you upload.</li>
      </ul>
    </div>
    <div
      class="relative w-full flex justify-center cursor-pointer rounded-lg border-2 border-dashed border-base-300 transition-all"
      :class="
        dragDropFocus
          ? 'border-primary bg-primary/10 scale-[1.01]'
          : 'hover:border-primary hover:bg-primary/5'
      "
      @dragover.prevent="updateDragDropFocus(true)"
      @dragleave.prevent="updateDragDropFocus(false)"
      @dragenter.prevent="updateDragDropFocus(true)"
      @drop.prevent="onFileChangeDrop"
    >
      <div class="text-center py-16">
        <p>
          <span class="text-4xl">
            <font-awesome-icon icon="upload" />
          </span>
        </p>
        <p class="mt-4">Drop the EML/MSG file here or click to upload</p>
        <p v-if="filename" class="mt-3">
          <span class="badge badge-primary gap-2">
            <font-awesome-icon icon="file-lines" class="w-3 h-3" />
            {{ filename }}
          </span>
        </p>
      </div>
      <input
        type="file"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        @change="onFileChange"
      />
    </div>
    <div class="text-center">
      <button class="btn btn-primary btn-lg" :disabled="analyzeTask.isRunning" @click="analyze">
        <font-awesome-icon
          v-if="analyzeTask.isRunning"
          icon="spinner"
          class="w-4 h-4 animate-spin"
        />
        <font-awesome-icon v-else icon="search" class="w-4 h-4" />
        {{ analyzeTask.isRunning ? 'Analyzing...' : 'Analyze' }}
      </button>
    </div>
  </div>
  <Divider />
  <ErrorMessage :error="analyzeTask.last?.error" v-if="analyzeTask.isError" />
  <Response
    :response="analyzeTask.last.value"
    v-if="analyzeTask.last?.value && !analyzeTask.isRunning"
  />
</template>
