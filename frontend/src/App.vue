<script setup lang="ts">
import { SignedIn, SignedOut, SignIn, useAuth } from '@clerk/vue'

import { setupAuthInterceptor } from '@/api'
import Navbar from '@/components/NavbarItem.vue'

const { getToken } = useAuth()
setupAuthInterceptor(() => getToken.value())
</script>

<template>
  <SignedIn>
    <Navbar />
    <section class="py-16">
      <div class="container mx-auto px-4">
        <router-view />
      </div>
    </section>
  </SignedIn>
  <SignedOut>
    <div class="flex min-h-screen items-center justify-center">
      <SignIn />
    </div>
  </SignedOut>
</template>
