<script setup lang="ts">
const route = useRoute()
</script>

<template>
  <a-layout class="app-shell">
    <a-layout-header class="app-header">
      <div class="brand">LDS 管線洩漏監測</div>
      <a-menu
        mode="horizontal"
        theme="dark"
        :selected-keys="[route.path]"
        class="nav-menu"
      >
        <a-menu-item key="/">
          <NuxtLink to="/">即時監測</NuxtLink>
        </a-menu-item>
        <a-menu-item key="/history">
          <NuxtLink to="/history">歷史查詢</NuxtLink>
        </a-menu-item>
      </a-menu>
    </a-layout-header>
    <a-layout-content class="app-content">
      <slot />
    </a-layout-content>
  </a-layout>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 10% 0%, rgba(11, 110, 79, 0.12), transparent 40%),
    linear-gradient(180deg, #f4f7f5 0%, #e8eee9 100%);
}

.app-header {
  display: flex;
  align-items: center;
  gap: 24px;
  background: #0b3d2e;
  padding: 0 24px;
}

.brand {
  color: #f5faf7;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  background: transparent;
  min-width: 0;
}

.nav-menu :deep(a) {
  color: inherit;
}

.app-content {
  padding: 24px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}
</style>
