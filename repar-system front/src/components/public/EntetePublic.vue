<script setup>
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import LogoReparSystem from '../commun/LogoReparSystem.vue'
import { routeAccueilUtilisateur, useAuthentification } from '../../services/serviceAuthentification'

const router = useRouter()
const { utilisateur, deconnecter } = useAuthentification()
const routeEspace = computed(() => routeAccueilUtilisateur(utilisateur.value))
const deconnexion = async () => {
  await deconnecter()
  await router.replace('/')
}
</script>
<template>
  <header class="header"><RouterLink class="brand" to="/"><LogoReparSystem :size="38"/><span>ReparSystem</span></RouterLink>
    <nav><RouterLink to="/">Accueil</RouterLink><RouterLink to="/reparateurs">Trouver un réparateur</RouterLink><RouterLink to="/diagnostic">Faire un diagnostic</RouterLink><RouterLink to="/devenir-reparateur">Devenir réparateur</RouterLink><a href="#about">À propos</a></nav>
    <div class="account">
      <template v-if="!utilisateur">
        <RouterLink to="/connexion">Connexion</RouterLink>
        <RouterLink class="signup" to="/inscription">S'inscrire</RouterLink>
      </template>
      <template v-else>
        <RouterLink class="account-link" :to="routeEspace">Mon espace</RouterLink>
        <button class="logout" type="button" @click="deconnexion">Déconnexion</button>
      </template>
    </div>
  </header>
</template>

<style scoped>
.account{gap:12px}.account-link,.logout{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:0 16px;border:1px solid #087f70;border-radius:9px;color:#087f70;background:transparent;font:inherit;font-size:12px;font-weight:700;white-space:nowrap}.logout{background:#087f70;color:#fff}.logout:hover{background:#06695e}@media(max-width:800px){.account>.account-link{display:inline-flex!important}.account>.logout{padding:0 10px;font-size:11px}}
</style>
