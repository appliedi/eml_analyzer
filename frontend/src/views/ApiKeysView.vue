<script setup lang="ts">
import { APIKeys } from '@clerk/vue'
</script>

<template>
  <div>
    <h2 class="mb-4 text-2xl font-bold">API Keys</h2>
    <p class="mb-6 text-sm opacity-70">
      Create API keys to access the EML Analyzer API from external applications. Use the key as a
      Bearer token: <code>Authorization: Bearer ak_...</code>
    </p>
    <APIKeys />
  </div>
</template>
