<template><AdministrationLayout search-placeholder="Rechercher un client…" v-slot="{search}"><section class="clients-page"><header class="title"><span><AppIcon name="users" :size="26"/></span><div><h1>Gestion des clients</h1><p>Liste des clients inscrits. Cliquez sur "Voir" pour consulter le profil et l'historique complet des demandes.</p></div></header><p v-if="erreur" class="error">{{ erreur }}</p><section class="filters"><b>Filtres :</b><button v-for="item in filters" :key="item.key" :class="{selected:active===item.key,blocked:item.key==='blocked'}" @click="active=item.key"><AppIcon :name="item.icon" :size="15"/> {{ item.label }}</button></section><TableauClients :clients="visible(search)" @view="selected=$event" @toggle="toggleClient"/><footer><span>Affichage de 1 à {{ visible(search).length }} sur {{ clients.length }} clients</span><div><button aria-label="Page précédente"><AppIcon name="chevron-left" :size="15"/></button><button class="current">1</button><button v-for="n in 4" :key="n">{{ n + 1 }}</button><button aria-label="Page suivante"><AppIcon name="chevron-right" :size="15"/></button></div></footer></section><FicheClient v-if="selected" :client="selected" @close="selected=null" @block="blockClient"/></AdministrationLayout></template>
<script setup>
import { computed, onMounted, ref } from 'vue'
import AdministrationLayout from '../../components/administrateur/AdministrationLayout.vue'
import TableauClients from '../../components/administrateur/TableauClients.vue'
import FicheClient from '../../components/administrateur/FicheClient.vue'
import { useClients } from '../../services/serviceClients'

const { clients, charger, toggle } = useClients()
const active = ref('all')
const selected = ref(null)
const erreur = ref('')

const filters = computed(() => [
  { key: 'all', icon: 'list', label: `Tous (${clients.value.length})` },
  { key: 'active', icon: 'check-circle', label: `Actifs (${clients.value.filter(item => item.status === 'Actif').length})` },
  { key: 'blocked', icon: 'x-circle', label: `Bloqués (${clients.value.filter(item => item.status === 'Bloqué').length})` },
])

const visible = search => clients.value.filter(client =>
  (active.value === 'all' || (active.value === 'active' && client.status === 'Actif') || (active.value === 'blocked' && client.status === 'Bloqué'))
  && JSON.stringify(client).toLowerCase().includes(search.toLowerCase())
)

async function toggleClient (client) {
  if (!client) return
  const action = client.status === 'Bloqué' ? 'débloquer' : 'bloquer'
  if (!window.confirm(`Voulez-vous ${action} le compte de ${client.name} ?`)) return
  try {
    await toggle(client)
    if (selected.value?.id === client.id) {
      selected.value = clients.value.find(item => item.id === client.id) || null
    }
  } catch (err) {
    erreur.value = err.message
  }
}

function blockClient () {
  if (!selected.value) return
  toggleClient(selected.value)
  selected.value = null
}

onMounted(async () => {
  try {
    await charger()
  } catch (err) {
    erreur.value = err.message
  }
})
</script>
<style scoped>.clients-page{display:grid;gap:17px;background:#fff;border:1px solid #dbeafa;border-radius:11px;padding:17px;box-shadow:0 4px 20px #114d970b}.title{min-height:90px;display:flex;align-items:center;gap:19px;padding:0 12px 17px;border-bottom:1px solid #e0edfa}.title>span{width:56px;height:56px;display:grid;place-items:center;border-radius:13px;background:#087f70;color:#fff;font-size:27px}.title h1{margin:0;text-transform:uppercase;color:#174b50;font-size:22px}.title p{margin:7px 0 0;color:#4b75c1;font-size:14px}.filters{height:80px;display:grid;grid-template-columns:80px repeat(3,214px);gap:24px;align-items:center;padding:0 22px;border:1px solid #d9eafb;border-radius:10px;background:#fff}.filters>b{color:#174b50}.filters button{height:45px;border:1px solid #bce5d7;border-radius:10px;background:#e9fbf3;color:#00a66a;font-size:14px}.filters button:first-of-type{background:#087f70;border-color:#087f70;color:#fff}.filters button.blocked{background:#fff0f3;border-color:#ffcbd4;color:#f33650}.filters button.selected{background:#087f70;border-color:#087f70;color:#fff;box-shadow:0 7px 14px #087f7032}.clients-page>footer{display:flex;justify-content:space-between;align-items:center;padding:0 14px;color:#5680c2;font-size:12px}.clients-page footer div{display:flex;gap:9px}.clients-page footer button{width:37px;height:37px;border:1px solid #d6e8fb;border-radius:8px;background:#fff;color:#2870d7}.clients-page footer .current{background:#087f70;color:#fff}.overlay{position:fixed;z-index:40;inset:0;background:#174b5055;display:grid;place-items:center}.overlay article{width:min(400px,calc(100% - 32px));background:#fff;border-radius:12px;color:#174b50;padding:22px;box-shadow:0 18px 45px #09285135}.overlay header{display:flex;justify-content:space-between;border-bottom:1px solid #e1ecfa;padding-bottom:13px}.overlay h2{margin:0;font-size:17px}.overlay header button{background:transparent;color:#087f70;font-size:27px}.overlay p{line-height:2;color:#4d74b4}.overlay .close{background:#087f70;color:#fff;border-radius:7px;padding:10px 15px;float:right}@media(max-width:900px){.filters{grid-template-columns:70px repeat(3,1fr);gap:10px;padding:0 12px}.title h1{font-size:18px}}@media(max-width:600px){.clients-page{padding:10px}.title{align-items:flex-start}.title h1{font-size:16px}.title p{font-size:11px}.filters{height:auto;padding:12px;grid-template-columns:1fr}.filters>b{display:none}}</style>
