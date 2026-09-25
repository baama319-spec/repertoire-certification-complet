<template>
  <div ref="menu" class="profil-client">
    <button class="declencheur" type="button" :aria-expanded="ouvert" @click="ouvert = !ouvert">
      <Avatar :photo="utilisateur?.photo_profil" :nom="nomComplet" :alt="`Photo de ${nomComplet}`" />
      <span>{{ nomComplet }}</span><b>⌄</b>
    </button>
    <nav v-if="ouvert" class="menu" aria-label="Menu du compte">
      <RouterLink to="/client/demandes" @click="fermer">▣ <span>Mes demandes</span></RouterLink>
      <RouterLink to="/client/avis" @click="fermer">☆ <span>Mes avis</span></RouterLink>
      <RouterLink to="/client/profil" @click="fermer">♟ <span>Mon profil</span></RouterLink>
      <RouterLink v-if="estReparateurVerifie" class="espace-pro" to="/pro/demandes" @click="fermer">⚒ <span>Espace réparateur</span></RouterLink>
      <button type="button" class="deconnexion" @click="seDeconnecter">⇥ <span>Déconnexion</span></button>
    </nav>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthentification } from '../../services/serviceAuthentification'
import Avatar from '../commun/Avatar.vue'
import { computed } from 'vue'

const router = useRouter()
const { deconnecter, utilisateur } = useAuthentification()
const nomComplet = computed(() => [utilisateur.value?.prenom, utilisateur.value?.nom].filter(Boolean).join(' ') || 'Mon compte')
const estReparateurVerifie = computed(() => utilisateur.value?.profil_reparateur?.profil_verifie)
const ouvert = ref(false)
const menu = ref(null)
const fermer = () => { ouvert.value = false }
const seDeconnecter = async () => {
  fermer()
  await deconnecter()
  router.replace('/')
}
const clicExterieur = (event) => { if (menu.value && !menu.value.contains(event.target)) fermer() }
onMounted(() => document.addEventListener('click', clicExterieur))
onBeforeUnmount(() => document.removeEventListener('click', clicExterieur))
</script>

<style scoped>
.profil-client{position:relative}.declencheur{display:flex;align-items:center;gap:8px;border:0;background:transparent;color:inherit;font:inherit;font-weight:700;cursor:pointer}.declencheur :deep(.avatar){width:32px;height:32px}.declencheur b{color:#6981a3}.menu{position:absolute;z-index:20;top:calc(100% + 10px);right:0;width:184px;padding:8px;border:1px solid #dceeea;border-radius:8px;background:#fff;box-shadow:0 10px 24px #1d4d861f}.menu a,.menu button{display:flex;align-items:center;gap:10px;width:100%;min-height:34px;padding:0 10px;border:0;border-radius:5px;background:transparent;color:#506f98;font:inherit;font-size:11px;text-align:left;cursor:pointer}.menu a:hover,.menu a.router-link-active{background:#e7f5f1;color:#087f70}.menu .espace-pro{margin-top:5px;border-top:1px solid #e8f0fa;color:#087f70;font-weight:700}.menu .deconnexion{margin-top:5px;padding-top:7px;border-top:1px solid #e8f0fa;color:#dd3951}.menu .deconnexion:hover{background:#fff0f2}.menu span{margin-left:2px}@media(max-width:700px){.declencheur span{display:none}.menu{right:-6px}}
</style>
