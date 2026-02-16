<script setup lang="ts">
import { computed, type PropType } from 'vue'

import Attachments from '@/components/attachments/AttachmentsItem.vue'
import Bodies from '@/components/bodies/BodiesItem.vue'
import CollapsibleSection from '@/components/CollapsibleSection.vue'
import EmailSummaryCard from '@/components/EmailSummaryCard.vue'
import Headers from '@/components/headers/HeadersItem.vue'
import ScorecardSection from '@/components/scorecard/ScorecardSection.vue'
import SectionNav from '@/components/SectionNav.vue'
import Verdicts from '@/components/verdicts/VerdictsItem.vue'
import { useStatus } from '@/composables/useStatus'
import type { ResponseType } from '@/schemas'

const props = defineProps({
  response: {
    type: Object as PropType<ResponseType>,
    required: true
  }
})

const { status } = useStatus()

const hasMalicious = computed(() => props.response.verdicts.some((v) => v.malicious))

const sections = computed(() => {
  const s: { id: string; label: string; icon: string; count?: number }[] = []
  if (props.response.verdicts.length > 0) {
    s.push({
      id: 'section-verdicts',
      label: 'Verdicts',
      icon: 'shield-halved',
      count: props.response.verdicts.length
    })
  }
  s.push({ id: 'section-headers', label: 'Headers', icon: 'envelope' })
  if (props.response.eml.bodies.length > 0) {
    s.push({
      id: 'section-bodies',
      label: 'Bodies',
      icon: 'file-lines',
      count: props.response.eml.bodies.length
    })
  }
  if (props.response.eml.attachments.length > 0) {
    s.push({
      id: 'section-attachments',
      label: 'Attachments',
      icon: 'paperclip',
      count: props.response.eml.attachments.length
    })
  }
  return s
})
</script>

<template>
  <div class="grid gap-4">
    <div v-if="status.cache" class="text-sm text-base-content/60">
      Cache ID:
      <router-link class="link link-info" :to="{ name: 'Lookup', params: { id: response.id } }">
        {{ response.id }}
      </router-link>
    </div>

    <ScorecardSection :response="response" />
    <EmailSummaryCard :header="response.eml.header" />
    <SectionNav :sections="sections" />

    <CollapsibleSection
      v-if="response.verdicts.length > 0"
      id="section-verdicts"
      title="Verdicts"
      icon="shield-halved"
      :default-open="hasMalicious"
      :count="response.verdicts.length"
    >
      <Verdicts :verdicts="response.verdicts" />
    </CollapsibleSection>

    <CollapsibleSection id="section-headers" title="Headers" icon="envelope" :default-open="false">
      <Headers class="grid gap-4" :header="response.eml.header" />
    </CollapsibleSection>

    <CollapsibleSection
      v-if="response.eml.bodies.length > 0"
      id="section-bodies"
      title="Bodies"
      icon="file-lines"
      :default-open="false"
      :count="response.eml.bodies.length"
    >
      <Bodies
        class="grid gap-4"
        :bodies="response.eml.bodies"
        :attachments="response.eml.attachments"
      />
    </CollapsibleSection>

    <CollapsibleSection
      v-if="response.eml.attachments.length > 0"
      id="section-attachments"
      title="Attachments"
      icon="paperclip"
      :default-open="false"
      :count="response.eml.attachments.length"
    >
      <Attachments class="grid gap-4" :attachments="response.eml.attachments" />
    </CollapsibleSection>
  </div>
</template>
