<script setup>
import { RouterLink } from 'vue-router'
import LogoReparSystem from '../commun/LogoReparSystem.vue'
</script>
<template>
  <header class="header"><RouterLink class="brand" to="/"><LogoReparSystem :size="38"/><span>ReparSystem</span></RouterLink>
    <nav><RouterLink to="/">Accueil</RouterLink><RouterLink to="/reparateurs">Trouver un réparateur</RouterLink><RouterLink to="/diagnostic">Faire un diagnostic</RouterLink><RouterLink to="/devenir-reparateur">Devenir réparateur</RouterLink><a href="#about">À propos</a></nav>
    <div class="account"><RouterLink to="/connexion">Connexion</RouterLink><RouterLink class="signup" to="/inscription">S'inscrire</RouterLink></div>
  </header>
</template>
