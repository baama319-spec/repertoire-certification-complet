<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import LayoutReparateur from '../../layouts/LayoutReparateur.vue'
import CarteAvisReparateur from '../../components/reparateur/CarteAvisReparateur.vue'
import { chargerAvis } from '../../services/serviceAvis'

const avisBruts = ref([])
const chargement = ref(true)
const erreur = ref('')
let intervalActualisation = null
let actualisationEnCours = false

const moyenne = computed(() => avisBruts.value.length
  ? avisBruts.value.reduce((total, avis) => total + Number(avis.note), 0) / avisBruts.value.length
  : 0)

const repartition = computed(() => {
  const comptes = [5, 4, 3, 2, 1].map(note => ({ note, nombre: avisBruts.value.filter(avis => Number(avis.note) === note).length }))
  const maximum = Math.max(...comptes.map(ligne => ligne.nombre), 1)
  return comptes.map(ligne => ({ ...ligne, largeur: `${ligne.nombre / maximum * 100}%` }))
})

const avis = computed(() => avisBruts.value.map(item => {
  const client = item.client_nom || 'Client'
  const note = Number(item.note)
  const date = item.date_creation ? new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long' }).format(new Date(item.date_creation)) : 'Date indisponible'
  return {
    id: item.id,
    client,
    initiales: client.split(/\s+/).map(part => part[0]).filter(Boolean).slice(0, 2).join('').toUpperCase(),
    note: note.toFixed(1),
    prestation: [item.demande_appareil, item.demande_specialite].filter(Boolean).join(' · ') || 'Réparation',
    texte: item.commentaire?.trim() || 'Le client a attribué une note à votre intervention, sans ajouter de commentaire.',
    date,
    lieu: item.demande_localisation || 'Localisation non renseignée',
  }
}))

const charger = async ({ silencieux = false } = {}) => {
  if (actualisationEnCours) return
  actualisationEnCours = true
  if (!silencieux) chargement.value = true
  if (!silencieux) erreur.value = ''
  try {
    avisBruts.value = await chargerAvis()
  } catch (requestError) {
    if (!silencieux || !avisBruts.value.length) erreur.value = requestError.message
  } finally {
    actualisationEnCours = false
    chargement.value = false
  }
}

const actualiserSiVisible = () => {
  if (document.visibilityState === 'visible') charger({ silencieux: true })
}

onMounted(() => {
  charger()
  intervalActualisation = window.setInterval(actualiserSiVisible, 10000)
  document.addEventListener('visibilitychange', actualiserSiVisible)
})

onBeforeUnmount(() => {
  if (intervalActualisation) window.clearInterval(intervalActualisation)
  document.removeEventListener('visibilitychange', actualiserSiVisible)
})
</script>
<template>
  <LayoutReparateur><section class="avis-page">
    <header class="titre"><span><AppIcon name="star" :size="24" fill="currentColor"/></span><div><h1>Avis et évaluations clients</h1></div></header>
    <section class="resume"><h2>Résumé des évaluations</h2><div class="notation"><article><AppIcon name="star" :size="34" fill="currentColor"/><strong>{{ moyenne.toFixed(1) }}</strong><em>/ 5.0</em><p>Basé sur <b>{{ avisBruts.length }}</b> avis</p></article><div class="barres"><p v-for="ligne in repartition" :key="ligne.note"><b>{{ ligne.note }}</b><AppIcon name="star" :size="15" fill="currentColor"/><i><small :style="{ width: ligne.largeur }"></small></i><em>({{ ligne.nombre }})</em></p></div></div></section>
    <section class="liste"><header><h2>Liste des derniers avis</h2><div><button type="button">Filtrer par note:　<b>Toutes</b>　⌄</button><button type="button">Trier par:　<b>Plus récents</b>　⌄</button></div></header><p v-if="chargement" class="etat">Chargement des avis…</p><p v-else-if="erreur" class="etat erreur" role="alert">{{ erreur }} <button type="button" @click="charger">Réessayer</button></p><p v-else-if="!avis.length" class="etat">Aucun avis reçu pour le moment. Les nouveaux avis de vos clients apparaîtront ici.</p><div v-else class="avis-liste"><CarteAvisReparateur v-for="item in avis" :key="item.id" :avis="item" /></div></section>
  </section></LayoutReparateur>
</template>
<style scoped>
.avis-page{max-width:1328px;margin:auto;padding:12px 18px 18px;background:#fff;border:1px solid #e0eaf7;border-radius:10px;box-shadow:0 2px 10px #1647820d;color:#0b3376}.titre{display:flex;align-items:center;gap:19px;padding:0 6px 22px}.titre>span{display:grid;place-items:center;width:55px;height:55px;border-radius:12px;background:#e6f1ff;color:#0873f7;font-size:32px}.titre h1,.resume h2,.liste h2{text-transform:uppercase;margin:0;font-size:21px}.titre p{margin:9px 0 0;color:#6684b6;font-size:17px}.resume,.liste{border:1px solid #d7e7fa;border-radius:9px;padding:17px;margin-bottom:20px}.resume h2{font-size:18px}.notation{display:grid;grid-template-columns:310px 1fr;gap:35px;margin-top:14px}.notation article{height:149px;padding:30px 24px;background:linear-gradient(135deg,#eaf4ff,#edf6ff);border-radius:8px;text-align:center}.notation article>b{color:#ffbd26;font-size:47px}.notation article strong{font-size:52px;margin-left:12px}.notation article em{color:#6a83ae;font-size:28px;font-style:normal}.notation article p{margin:13px 0 0;color:#6480ac;font-size:16px}.barres{padding-top:0}.barres p{display:grid;grid-template-columns:18px 25px 1fr 70px;align-items:center;gap:5px;margin:7px 0;font-size:15px}.barres p>span{color:#ffbd26;font-size:18px}.barres i{height:11px;border-radius:8px;background:#e8f0fb;overflow:hidden}.barres i small{display:block;height:100%;border-radius:8px;background:linear-gradient(90deg,#3188f6,#3488ee)}.barres em{color:#6b85ae;font-style:normal}.liste{padding:13px 17px 18px;margin:0}.liste>header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.liste>header h2{font-size:18px}.liste>header div{display:flex;gap:20px}.liste button{height:39px;padding:0 13px;border:1px solid #d2e3f9;border-radius:9px;background:#fff;color:#5976a4;font-size:12px}.liste button b{color:#0d3676}.avis-liste{display:grid;gap:17px}@media(max-width:1000px){.notation{grid-template-columns:250px 1fr}.liste>header{align-items:flex-start;gap:14px;flex-direction:column}}@media(max-width:700px){.avis-page{padding:12px}.titre{align-items:flex-start}.titre>span{width:45px;height:45px;font-size:25px}.titre h1{font-size:17px}.titre p{font-size:13px}.notation{grid-template-columns:1fr}.notation article{height:auto}.liste>header div{gap:6px;flex-wrap:wrap}.barres p{grid-template-columns:18px 22px 1fr 42px}}
.etat{margin:0;padding:24px;border:1px dashed #d7e7fa;border-radius:9px;color:#6684b6;text-align:center;font-size:13px}.etat.erreur{color:#a52e3a}.etat button{margin-left:10px;color:#087f70;font-weight:700;cursor:pointer}
</style>
