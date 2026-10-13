<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import LogoReparSystem from '../commun/LogoReparSystem.vue'
import { actualiserUtilisateur, routeAccueilUtilisateur, useAuthentification } from '../../services/serviceAuthentification'

const router = useRouter()
const { utilisateur, deconnecter } = useAuthentification()
const routeEspace = computed(() => routeAccueilUtilisateur(utilisateur.value))
const deconnexion = async () => {
  await deconnecter()
  await router.replace('/')
}
const actualiserCompte = () => {
  if (document.visibilityState === 'visible') actualiserUtilisateur().catch(() => {})
}
onMounted(() => {
  document.addEventListener('visibilitychange', actualiserCompte)
  window.addEventListener('focus', actualiserCompte)
  actualiserCompte()
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', actualiserCompte)
  window.removeEventListener('focus', actualiserCompte)
})
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
.header {
  height: 70px;
  display: flex;
  align-items: center;
  gap: 60px;
  padding: 0 max(5.5%, 48px);
  background: #111827;
  border-bottom: 1px solid rgba(255,255,255,.16);
  position: relative;
  z-index: 3;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 17px;
  font-weight: 800;
  white-space: nowrap;
}
.header nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 34px;
  margin: auto;
  font-size: 12px;
  font-weight: 600;
}
.header nav a {
  color: #fff;
  transition: color .2s ease;
}
.header nav a:hover,
.header nav a.router-link-exact-active {
  color: #087f70;
}
.account {
  display: flex;
  align-items: center;
  gap: 12px;
}
.account > a {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}
.account-link,.logout {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0 16px;
  border: 1px solid rgba(255,255,255,.18);
  border-radius: 9px;
  color: #fff;
  background: transparent;
  font: inherit;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.logout {
  background: #087f70;
  border-color: #087f70;
  color: #fff;
}
.logout:hover {
  background: #06695e;
}
.signup {
  padding: 12px 24px;
  border-radius: 9px;
  background: #087f70;
  color: white;
  border: 1px solid #087f70;
}
@media(max-width:800px){
  .header{padding:0 20px;height:62px;gap:10px}
  .header nav{display:none}
  .account{margin-left:auto;gap:9px}
  .account>.account-link{display:inline-flex!important}
  .account>.logout{padding:0 10px;font-size:11px}
}
</style>
