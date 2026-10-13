<script setup>
import BarreLateraleReparateur from '../components/reparateur/BarreLateraleReparateur.vue'
import EnteteReparateur from '../components/reparateur/EnteteReparateur.vue'
</script>
<template><div class="espace-pro"><BarreLateraleReparateur/><div class="contenu-pro"><EnteteReparateur/><main><slot /></main></div></div></template>
<style scoped>.espace-pro{min-height:100vh;display:flex;background:#f5faf8}.contenu-pro{min-width:0;flex:1}.contenu-pro>main{padding:29px 20px 55px}@media(max-width:700px){.contenu-pro>main{padding:12px 9px}}</style>
