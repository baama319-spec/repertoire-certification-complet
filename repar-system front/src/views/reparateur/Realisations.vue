<script setup>
import { onMounted, ref } from 'vue'
import LayoutReparateur from '../../layouts/LayoutReparateur.vue'
import CarteRealisation from '../../components/reparateur/CarteRealisation.vue'
import AjouterRealisationModal from '../../modales/reparateur/AjouterRealisationModal.vue'
import { chargerRealisations, supprimerRealisation } from '../../services/serviceRealisations'
const modaleOuverte=ref(false), realisations=ref([]), chargement=ref(true), erreur=ref('')
const charger=async()=>{chargement.value=true;try{realisations.value=await chargerRealisations()}catch(e){erreur.value=e.message}finally{chargement.value=false}}
const supprimer=async realisation=>{if(!window.confirm(`Supprimer « ${realisation.titre} » ?`))return;try{await supprimerRealisation(realisation.id);realisations.value=realisations.value.filter(item=>item.id!==realisation.id)}catch(e){erreur.value=e.message}}
onMounted(charger)
</script>
<template><LayoutReparateur><section class="portfolio"><header><div><h1>▧ Mes réalisations publiques</h1><p>Mettez en avant vos réparations réussies pour rassurer vos futurs clients.</p></div><button @click="modaleOuverte=true">＋ Ajouter une réalisation</button></header><p v-if="chargement||erreur||!realisations.length" class="etat">{{ chargement ? 'Chargement…' : erreur || 'Vous n’avez pas encore publié de réalisation.' }}</p><section v-else class="grille"><CarteRealisation v-for="item in realisations" :key="item.id" :realisation="item" @supprimer="supprimer"/></section></section><AjouterRealisationModal v-if="modaleOuverte" @fermer="modaleOuverte=false" @publie="item=>{realisations.unshift(item);modaleOuverte=false}"/></LayoutReparateur></template>
<style scoped>.portfolio{max-width:1328px;min-height:760px;margin:auto;background:#fff;border:1px solid #e5edf8;border-radius:10px}.portfolio>header{display:flex;justify-content:space-between;gap:20px;padding:28px;border-bottom:1px solid #e6edf7;color:#0a2d68}.portfolio h1{margin:4px 0 12px;font-size:22px}.portfolio p{margin:0;color:#6a82a9}.portfolio header button{height:52px;padding:0 26px;border:0;border-radius:9px;background:#0666e8;color:#fff;font-weight:700}.grille{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;padding:17px}.etat{padding:44px 28px}@media(max-width:800px){.portfolio>header{flex-direction:column}.portfolio header button{width:100%}.grille{grid-template-columns:1fr}}</style>
