<template>
  <img v-if="photo" class="avatar" :src="photo" :alt="alt" @error="imageIndisponible = true">
  <span v-else class="avatar avatar-defaut" :aria-label="alt">{{ initiales }}</span>
</template>

<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ photo: { type: String, default: '' }, nom: { type: String, default: '' }, alt: { type: String, default: 'Photo de profil' } })
const imageIndisponible = ref(false)
const initiales = computed(() => props.nom.split(/\s+/).filter(Boolean).slice(0, 2).map(m => m[0]).join('').toUpperCase() || 'RS')
const photo = computed(() => imageIndisponible.value ? '' : props.photo)
</script>

<style scoped>
.avatar{display:grid;place-items:center;width:100%;height:100%;border-radius:50%;object-fit:cover;background:#e5f0ff}.avatar-defaut{color:#087f70;font-weight:800}
</style>
