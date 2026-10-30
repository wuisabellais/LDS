<script setup lang="ts">
const theme = {
  token: {
    colorPrimary: '#0b6e4f',
    borderRadius: 6,
    fontFamily: '"Noto Sans TC", "Segoe UI", sans-serif',
  },
}
</script>

<template>
  <a-config-provider :theme="theme">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </a-config-provider>
</template>
