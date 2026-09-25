<template><AdministrationLayout search-placeholder="Rechercher un réparateur…" v-slot="{search}"><section class="page"><header class="title"><span>♟</span><div><h1>Gestion des réparateurs</h1><p>Consultez les candidatures réelles et validez les profils professionnels.</p></div></header><p v-if="erreur" class="erreur">{{ erreur }}</p><section class="filters"><b>Filtres :</b><button v-for="f in filters" :key="f" :class="{active:f===filter}" @click="filter=f">{{f}}</button></section><TableauReparateurs :reparateurs="visible(search)" @verify="selected=$event" @block="changerBlocage"/><footer><span>Affichage de {{ reparateurs.length }} réparateur(s)</span></footer></section><FicheReparateur v-if="selected" :reparateur="selected" @close="selected=null" @validate="validate" @certify="certifier"/></AdministrationLayout></template>
<script setup>
import { onMounted, ref } from 'vue'
import AdministrationLayout from '../../components/administrateur/AdministrationLayout.vue'
import TableauReparateurs from '../../components/administrateur/TableauReparateurs.vue'
import FicheReparateur from '../../components/administrateur/FicheReparateur.vue'
import { useReparateurs } from '../../services/serviceReparateurs'
const { reparateurs, charger, verifier, certifierPro, bloquer } = useReparateurs()
const filter = ref('Tous'), selected = ref(null), erreur = ref('')
const filters = ['Tous', 'Certifiés Pro', 'En attente', 'Compte bloqué']
const visible = q => reparateurs.value.filter(r => (filter.value === 'Tous' || r.status === filter.value) && JSON.stringify(r).toLowerCase().includes(q.toLowerCase()))
async function validate ({ statut, motif }) {
  try { await verifier(selected.value, statut, motif); selected.value = null } catch (err) { erreur.value = err.message }
}
async function certifier () { try { await certifierPro(selected.value); selected.value = null } catch (err) { erreur.value = err.message } }
async function changerBlocage (reparateur) {
  const action = reparateur.estBloque ? 'réactiver' : 'bloquer'
  if (!window.confirm(`Voulez-vous ${action} le compte de ${reparateur.name} ?`)) return
  try { await bloquer(reparateur, !reparateur.estBloque) } catch (err) { erreur.value = err.message }
}
onMounted(async () => { try { await charger() } catch (err) { erreur.value = err.message } })
</script>
<style scoped>.page{display:grid;gap:17px;background:#fff;border:1px solid #e2eefb;border-radius:11px;padding:16px}.title{height:80px;display:flex;align-items:center;gap:20px;border-bottom:1px solid #e5effa}.title>span{width:54px;height:54px;display:grid;place-items:center;border-radius:13px;background:#087f70;color:#fff;font-size:27px}.title h1{margin:0;text-transform:uppercase;color:#174b50;font-size:22px}.title p{margin:7px 0;color:#5275af;font-size:15px}.title button{margin-left:auto;background:#087f70;color:#fff;padding:15px 20px;border-radius:9px}.filters{display:grid;grid-template-columns:80px repeat(4,1fr);gap:25px;align-items:center}.filters button{height:45px;border:1px solid #c6ddff;border-radius:10px;background:#edfcf7;color:#00a879}.filters button:nth-of-type(3){background:#fff5e2;color:#e68b00}.filters button:nth-of-type(4){background:#fff0f2;color:#f03650}.filters button.active{background:#087f70;color:#fff}.page>footer{height:32px;display:flex;justify-content:space-between;color:#6381b5;font-size:13px}.page footer b{background:#087f70;color:#fff;padding:9px 12px;border-radius:7px}</style>
