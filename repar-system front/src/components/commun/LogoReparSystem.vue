<script setup>
import logo from '../../assets/images/logo-removebg-preview(1).png'

defineProps({
  size: { type: [Number, String], default: 40 },
  alt: { type: String, default: 'Logo ReparSystem' },
})
</script>

<template>
  <img class="logo-reparsystem" :src="logo" :alt="alt" :style="{ width: `${size}px`, height: `${size}px` }">
</template>

<style scoped>
.logo-reparsystem { display: block; flex: 0 0 auto; object-fit: contain; }
</style>
