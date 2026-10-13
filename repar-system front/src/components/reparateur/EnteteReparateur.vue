<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthentification } from '../../services/serviceAuthentification'
import Avatar from '../commun/Avatar.vue'
const route = useRoute()
const router = useRouter()
const recherche = computed(() => route.path.includes('realisations') ? 'Rechercher dans le portfolio...' : route.path.includes('avis') ? 'Rechercher dans les avis...' : route.path.includes('profil') ? 'Rechercher dans les paramètres...' : 'Rechercher une demande...')
const { utilisateur, deconnecter } = useAuthentification()
const nomComplet = computed(() => [utilisateur.value?.prenom, utilisateur.value?.nom].filter(Boolean).join(' ') || 'Mon compte')
const ouvert = ref(false)
const menu = ref(null)
const fermer = () => { ouvert.value = false }
const passerClient = () => { fermer(); router.push('/client/demandes') }
const seDeconnecter = async () => {
  fermer()
  await deconnecter()
  router.replace('/')
}
const clicExterieur = (event) => { if (menu.value && !menu.value.contains(event.target)) fermer() }
onMounted(() => document.addEventListener('click', clicExterieur))
onBeforeUnmount(() => document.removeEventListener('click', clicExterieur))
</script>
<template>
  <header class="entete-pro"><label><AppIcon name="search" :size="18"/><input :placeholder="recherche" /></label><div class="outils"><button class="notification" aria-label="Notifications"><AppIcon name="bell" :size="21"/><sup>3</sup></button><span class="separateur"></span><div ref="menu" class="profil-pro"><button type="button" class="declencheur" :aria-expanded="ouvert" @click="ouvert = !ouvert"><Avatar class="mini-avatar" :photo="utilisateur?.photo_profil" :nom="nomComplet" :alt="`Photo de ${nomComplet}`"/><span class="identite"><b>{{ nomComplet }}</b><small>(Réparateur)</small></span><AppIcon name="chevron-down" :size="14"/></button><nav v-if="ouvert" class="menu" aria-label="Menu du compte"><button type="button" class="espace-client" @click="passerClient"><AppIcon name="users" :size="15"/> <span>Passer à l’espace client</span></button><button type="button" class="deconnexion" @click="seDeconnecter"><AppIcon name="logout" :size="15"/> <span>Déconnexion</span></button></nav></div></div></header>
</template>
<style scoped>
.entete-pro{height:82px;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 23px 0 70px;box-shadow:0 2px 10px rgba(18,63,69,.08);position:relative;z-index:1}.entete-pro label{height:53px;width:595px;display:flex;align-items:center;gap:15px;padding:0 18px;border:1px solid #dfeee8;background:#f9fdfb;border-radius:17px;color:#123f45;font-size:24px}.entete-pro input{border:0;outline:0;background:transparent;width:100%;font:inherit;font-size:15px;color:#123f45}.outils{display:flex;align-items:center;gap:21px;color:#123f45}.notification{position:relative;border:0;background:transparent;color:#087f70;font-size:27px}.notification sup{display:grid;place-items:center;position:absolute;top:0;right:-9px;width:19px;height:19px;border-radius:50%;background:#ff4356;color:#fff;font-size:11px}.separateur{width:1px;height:43px;background:#e2f1ee}.profil-pro{position:relative}.declencheur{display:flex;align-items:center;gap:13px;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer}.mini-avatar{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#087f70;color:#fff;font-size:12px;font-weight:800}.identite{display:grid;font-size:13px}.identite small{color:#5d7d7d;font-size:12px}.fleche{font-size:21px}.menu{position:absolute;z-index:20;top:calc(100% + 10px);right:0;width:220px;padding:8px;border:1px solid #dfeee8;border-radius:8px;background:#fff;box-shadow:0 10px 24px rgba(9,127,112,.08)}.menu button{display:flex;align-items:center;gap:10px;width:100%;min-height:36px;padding:0 10px;border:0;border-radius:5px;background:transparent;color:#45696a;font:inherit;font-size:11px;text-align:left;cursor:pointer}.menu .espace-client{color:#087f70;font-weight:700}.menu .espace-client:hover{background:#e7f5f1}.menu .deconnexion{margin-top:5px;padding-top:7px;border-top:1px solid #edf6f4;color:#dd3951}.menu .deconnexion:hover{background:#fff0f2}@media(max-width:1000px){.entete-pro{padding-left:25px}.entete-pro label{width:42vw}}@media(max-width:700px){.entete-pro{height:62px;padding:0 10px}.entete-pro label{height:38px;width:45vw;font-size:18px}.identite,.separateur{display:none}.outils{gap:8px}.declencheur{gap:4px}.mini-avatar{width:38px;height:38px}.menu{right:-6px}}
</style>
