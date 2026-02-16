<script setup lang="ts">
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import { type PropType } from 'vue'

import ReportAttachments from '@/components/report/ReportAttachments.vue'
import ReportBodies from '@/components/report/ReportBodies.vue'
import ReportEmailSummary from '@/components/report/ReportEmailSummary.vue'
import ReportHeaders from '@/components/report/ReportHeaders.vue'
import ReportRiskSummary from '@/components/report/ReportRiskSummary.vue'
import ReportVerdicts from '@/components/report/ReportVerdicts.vue'
import type { ResponseType } from '@/schemas'

dayjs.extend(utc)

const props = defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})

const generatedAt = dayjs.utc().format()

const handlePrint = () => {
  window.print()
}
</script>

<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold">EML Analysis Report</h1>
      <p class="text-base-content/60 mt-1">Analysis ID: {{ props.response.id }}</p>
      <p class="text-base-content/60">Generated: {{ generatedAt }}</p>
      <div class="flex gap-2 mt-3 print:hidden">
        <button class="btn btn-sm btn-primary gap-2" @click="handlePrint">
          <font-awesome-icon icon="print" class="w-4 h-4" />
          Print Report
        </button>
        <router-link
          :to="{ name: 'Lookup', params: { id: props.response.id } }"
          class="btn btn-sm btn-outline"
        >
          Back to Analysis
        </router-link>
      </div>
    </div>

    <section class="report-section">
      <h2 class="text-2xl font-bold mb-4">Risk Summary</h2>
      <ReportRiskSummary :response="props.response" />
    </section>

    <section class="report-section mt-8">
      <h2 class="text-2xl font-bold mb-4">Email Summary</h2>
      <ReportEmailSummary :header="props.response.eml.header" />
    </section>

    <section class="report-section mt-8" v-if="props.response.verdicts.length > 0">
      <h2 class="text-2xl font-bold mb-4">Verdicts</h2>
      <ReportVerdicts :verdicts="props.response.verdicts" />
    </section>

    <section class="report-section mt-8">
      <h2 class="text-2xl font-bold mb-4">Headers</h2>
      <ReportHeaders :header="props.response.eml.header" />
    </section>

    <section class="report-section mt-8" v-if="props.response.eml.bodies.length > 0">
      <h2 class="text-2xl font-bold mb-4">Bodies</h2>
      <ReportBodies :bodies="props.response.eml.bodies" />
    </section>

    <section class="report-section mt-8" v-if="props.response.eml.attachments.length > 0">
      <h2 class="text-2xl font-bold mb-4">Attachments</h2>
      <ReportAttachments :attachments="props.response.eml.attachments" />
    </section>
  </div>
</template>
