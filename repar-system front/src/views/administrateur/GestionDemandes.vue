<template>
  <AdministrationLayout search-placeholder="N° de demande, client…" v-slot="{ search }">
    <section class="demandes">
      <header class="title">
        <span><AppIcon name="clipboard" :size="22"/></span>
        <div>
          <h1>Supervision des demandes</h1>
          <p>Consultez et gérez les demandes de réparation enregistrées dans l’application.</p>
        </div>
        <button class="refresh" type="button" :disabled="loading" @click="charger">
          <AppIcon name="activity" :size="15"/> {{ loading ? 'Actualisation…' : 'Actualiser' }}
        </button>
      </header>

      <p v-if="error" class="feedback error" role="alert">
        {{ error }}
        <button type="button" @click="charger">Réessayer</button>
      </p>

      <section class="filters" aria-label="Filtrer par statut">
        <b>Filtres :</b>
        <button
          v-for="filter in filters"
          :key="filter.key"
          type="button"
          :class="[filter.key, { selected: active === filter.key }]"
          @click="selectFilter(filter.key)"
        >
          <AppIcon :name="filter.icon" :size="15"/> {{ filter.label }} ({{ counts[filter.key] }})
        </button>
      </section>

      <p v-if="loading && !demandes.length" class="feedback">Chargement des demandes…</p>
      <TableauDemandes
        v-else
        :demandes="paginated"
        @detail="selected = $event"
        @delete="removeItem"
      />

      <footer class="bottom">
        <span>
          Affichage de {{ startItem }} à {{ endItem }} sur {{ filtered.length }} demande{{ filtered.length > 1 ? 's' : '' }}
          <template v-if="total !== filtered.length"> ({{ total }} au total)</template>
        </span>
        <nav class="pagination" aria-label="Pagination des demandes">
          <button type="button" aria-label="Page précédente" :disabled="page === 1" @click="page--"><AppIcon name="chevron-left" :size="16"/></button>
          <button
            v-for="number in pageNumbers"
            :key="number"
            type="button"
            :class="{ current: number === page }"
            :aria-current="number === page ? 'page' : undefined"
            @click="page = number"
          >{{ number }}</button>
          <button type="button" aria-label="Page suivante" :disabled="page >= pageCount" @click="page++"><AppIcon name="chevron-right" :size="16"/></button>
        </nav>
      </footer>
    </section>

    <DetailDemandeModal v-if="selected" :demande="selected" @close="selected = null" />
  </AdministrationLayout>
</template>

<script setup>
import { computed, inject, onMounted, onUnmounted, ref, watch } from 'vue'
import AdministrationLayout from '../../components/administrateur/AdministrationLayout.vue'
import TableauDemandes from '../../components/administrateur/TableauDemandes.vue'
import DetailDemandeModal from '../../modales/administrateur/DetailDemandeModal.vue'
import { chargerDemandesAdministration, supprimerDemandeAdministration } from '../../services/serviceDemandes'

const demandes = ref([])
const total = ref(0)
const loading = ref(true)
const error = ref('')
const active = ref('all')
const selected = ref(null)
const page = ref(1)
const pageSize = 20
const searchValue = inject('administrationSearch', ref(''))
let refreshTimer

const statusMap = {
  EN_ATTENTE: 'En attente',
  ACCEPTEE: 'Acceptée',
  REFUSEE: 'Refusée',
  ANNULEE: 'Annulée',
}

const filters = [
  { key: 'all', icon: 'list', label: 'Toutes' },
  { key: 'EN_ATTENTE', icon: 'clock', label: 'En attente' },
  { key: 'ACCEPTEE', icon: 'check-circle', label: 'Acceptées' },
  { key: 'ANNULEE', icon: 'close', label: 'Annulées' },
  { key: 'REFUSEE', icon: 'x-circle', label: 'Refusées' },
]

function formatRequest (request) {
  const created = request.date_creation ? new Date(request.date_creation) : null
  const validDate = created && !Number.isNaN(created.getTime())
  const status = statusMap[request.statut] || request.statut || 'Inconnu'
  const client = request.client_detail || {}
  const location = request.localisation_detail || {}
  const device = request.appareil || 'Réparation'
  return {
    ...request,
    status,
    date: validDate ? new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(created) : 'Date inconnue',
    time: validDate ? new Intl.DateTimeFormat('fr-FR', { timeStyle: 'short' }).format(created) : '',
    client: client.nom || 'Client',
    phone: client.telephone || 'Téléphone non renseigné',
    zone: [location.quartier, location.ville].filter(Boolean).join(', ') || location.nom || 'Zone non renseignée',
    device,
    issue: request.specialite_detail?.nom || request.description_probleme || 'Réparation générale',
    icon: /télé|smartphone|mobile/i.test(device) ? 'smartphone' : /ordinateur|pc/i.test(device) ? 'laptop' : 'wrench',
  }
}

const counts = computed(() => ({
  all: total.value,
  EN_ATTENTE: demandes.value.filter(item => item.statut === 'EN_ATTENTE').length,
  ACCEPTEE: demandes.value.filter(item => item.statut === 'ACCEPTEE').length,
  ANNULEE: demandes.value.filter(item => item.statut === 'ANNULEE').length,
  REFUSEE: demandes.value.filter(item => item.statut === 'REFUSEE').length,
}))

const filtered = computed(() => {
  const term = String(searchValue.value || '').trim().toLocaleLowerCase('fr')
  return demandes.value
    .filter(item => active.value === 'all' || item.statut === active.value)
    .map(formatRequest)
    .filter(item => !term || [item.id, item.client, item.phone, item.device, item.issue, item.zone, item.status].join(' ').toLocaleLowerCase('fr').includes(term))
})

const paginated = computed(() => filtered.value.slice((page.value - 1) * pageSize, page.value * pageSize))
const pageCount = computed(() => Math.max(1, Math.ceil(filtered.value.length / pageSize)))
const pageNumbers = computed(() => Array.from({ length: Math.min(5, pageCount.value) }, (_, index) => {
  const first = Math.min(Math.max(page.value - 2, 1), Math.max(pageCount.value - 4, 1))
  return first + index
}))
const startItem = computed(() => filtered.value.length ? (page.value - 1) * pageSize + 1 : 0)
const endItem = computed(() => Math.min(page.value * pageSize, filtered.value.length))

async function charger () {
  loading.value = true
  error.value = ''
  try {
    const result = await chargerDemandesAdministration()
    demandes.value = result.demandes
    total.value = result.statistiques.demandes_totales ?? result.demandes.length
    if (page.value > pageCount.value) page.value = pageCount.value
  } catch (err) {
    error.value = err.message || 'Impossible de charger les demandes.'
  } finally {
    loading.value = false
  }
}

async function removeItem (item) {
  if (!window.confirm(`Supprimer définitivement la demande ${item.id} ?`)) return
  error.value = ''
  try {
    await supprimerDemandeAdministration(item.id)
    demandes.value = demandes.value.filter(demande => demande.id !== item.id)
    total.value = Math.max(0, total.value - 1)
    if (selected.value?.id === item.id) selected.value = null
    if (page.value > pageCount.value) page.value = pageCount.value
  } catch (err) {
    error.value = err.message || 'La suppression de la demande a échoué.'
  }
}

function selectFilter (key) {
  active.value = key
  page.value = 1
}

// Keep the admin list current while the page stays open.
onMounted(() => {
  charger()
  refreshTimer = window.setInterval(charger, 30000)
})
onUnmounted(() => window.clearInterval(refreshTimer))
watch(filtered, () => { if (page.value > pageCount.value) page.value = pageCount.value })
</script>

<style scoped>
.demandes{display:grid;gap:19px}.title,.filters{background:#fff;border:1px solid #dfecfa;border-radius:10px}.title{min-height:102px;display:flex;align-items:center;gap:20px;padding:20px 23px}.title>span{width:53px;height:53px;flex:none;display:grid;place-items:center;border-radius:13px;background:#087f70;color:#fff;font-size:27px}.title h1{text-transform:uppercase;font-size:24px;line-height:1.15;margin:0;color:#092d73}.title p{margin:9px 0 0;color:#5275af;font-size:14px}.refresh{margin-left:auto;padding:11px 15px;border:1px solid #bcd8f7;border-radius:8px;background:#fff;color:#087f70;font-weight:700;white-space:nowrap}.refresh:disabled{opacity:.6}.filters{min-height:74px;display:flex;flex-wrap:nowrap;gap:12px;align-items:center;padding:14px 19px;overflow-x:auto}.filters>b{flex:none;margin-right:8px;font-size:15px;color:#174b50;white-space:nowrap}.filters button{flex:1 0 145px;min-width:145px;height:44px;padding:0 12px;border:1px solid #c6ddff;border-radius:10px;background:#f4f9ff;color:#087f70;font-size:13px;font-weight:700;white-space:nowrap}.filters button.selected{background:#087f70;border-color:#087f70;color:#fff;box-shadow:0 7px 15px #087f7037}.filters button.EN_ATTENTE{background:#fff5e2;border-color:#ffe0a6;color:#c37a00}.filters button.ACCEPTEE{background:#eff8ff}.filters button.ANNULEE,.filters button.REFUSEE{background:#edfcf7;border-color:#c7f1df;color:#008b68}.filters button.selected{background:#087f70;border-color:#087f70;color:#fff}.feedback{padding:18px;border:1px solid #dceafa;border-radius:9px;background:#fff;color:#6181b6}.feedback.error{color:#b4233b;border-color:#ffd3da}.feedback button{margin-left:10px;color:#087f70;font-weight:700}.bottom{min-height:59px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:12px;padding:5px 12px;color:#6181b6;font-size:13px}.pagination{display:flex;gap:8px}.pagination button{width:36px;height:36px;border-radius:8px;border:1px solid #d3e4fa;background:#fff;color:#087f70}.pagination button.current{background:#087f70;color:#fff}.pagination button:disabled{opacity:.45;cursor:not-allowed}@media(max-width:700px){.title{align-items:flex-start;flex-wrap:wrap}.title h1{font-size:18px}.title p{font-size:12px}.refresh{margin-left:73px}.filters{align-items:center}.filters>b{width:auto}.filters button{flex:0 0 145px;min-width:145px}.bottom{align-items:flex-start}.pagination{flex-wrap:wrap}}
@media(min-width:701px){.filters{display:grid;grid-template-columns:82px repeat(5,minmax(0,1fr));gap:10px;overflow:visible}.filters>b{margin:0}.filters button{width:100%;min-width:0;padding:0 5px;font-size:12px}}
@media(max-width:700px){.filters{display:flex;flex-wrap:nowrap;overflow-x:auto}.filters>b{width:auto}.filters button{flex:0 0 145px;min-width:145px}}
</style>