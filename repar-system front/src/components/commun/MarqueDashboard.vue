<script setup>
import LogoReparSystem from './LogoReparSystem.vue'

defineProps({
  role: { type: String, default: '' },
  size: { type: Number, default: 58 },
  textSize: { type: Number, default: 23 },
  tone: { type: String, default: 'light' },
})
</script>

<template>
  <span class="dashboard-brand" :class="`brand-${tone}`" :style="{ '--tile-size': `${size}px`, '--text-size': `${textSize}px` }">
    <span class="brand-tile"><LogoReparSystem :size="size - 12" /></span>
    <span class="dashboard-brand-label"><strong>ReparSystem</strong><span v-if="role">{{ role }}</span></span>
  </span>
</template>

<style scoped>
.dashboard-brand { display: inline-flex; min-width: 0; align-items: center; gap: 12px; color: #fff; white-space: nowrap; }
.brand-tile { display: grid; width: var(--tile-size); height: var(--tile-size); flex: 0 0 var(--tile-size); place-items: center; overflow: hidden; border-radius: 12px; background: #fff; }
.brand-tile :deep(.logo-reparsystem) { width: calc(var(--tile-size) - 12px) !important; height: calc(var(--tile-size) - 12px) !important; padding: 0; object-fit: contain; }
.dashboard-brand-label { display: inline-flex; min-width: 0; align-items: baseline; gap: 5px; font-size: var(--text-size); letter-spacing: -.7px; }
.dashboard-brand-label strong { font-weight: 750; }
.dashboard-brand-label > span { font-weight: 400; }
.brand-dark { color: #12376c; }
</style>
