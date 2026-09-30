<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import { api } from '../../services/api'
import { chargerRealisations } from '../../services/serviceRealisations'

const route = useRoute()
const router = useRouter()
const active = ref('about'), reparateur = ref(null), realisations = ref([]), chargement = ref(false)
const slug = nom => (nom || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
const nom = computed(() => reparateur.value ? [reparateur.value.utilisateur_detail?.prenom, reparateur.value.utilisateur_detail?.nom].filter(Boolean).join(' ') : '')
const specialites = computed(() => reparateur.value?.specialites_detail || [])
const zones = computed(() => (reparateur.value?.zones_intervention_detail || []).map(zone => [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ')))
const image = computed(() => reparateur.value?.utilisateur_detail?.photo_profil || '')
const charger = async () => {
  chargement.value = true
  try {
    const data = await api('/reparateurs/')
    const liste = data.results || data
    reparateur.value = liste.find(item => String(item.id) === String(route.params.slug) || slug(`${item.utilisateur_detail?.prenom || ''} ${item.utilisateur_detail?.nom || ''}`) === route.params.slug) || null
    realisations.value = reparateur.value ? await chargerRealisations(reparateur.value.id) : []
  } finally { chargement.value = false }
}
onMounted(charger)
watch(() => route.params.slug, charger)
const demanderIntervention = () => router.push({ name: 'demande-reparation', query: { reparateur: reparateur.value.id } })
</script>

<template>
  <EntetePublic />
  <main class="detail-page">
    <RouterLink class="back" to="/reparateurs">← Retour aux réparateurs</RouterLink>
    <p v-if="chargement">Chargement du profil…</p>
    <template v-else-if="reparateur">
      <section class="detail-hero">
        <div class="detail-image" :style="image ? { backgroundImage: `url(${image})` } : {}"><span v-if="!image">{{ nom.slice(0, 1) }}</span></div>
        <div class="detail-info">
          <span class="eyebrow">RÉPARATEUR VÉRIFIÉ</span>
          <h1>{{ nom }} <i>✓</i></h1>
          <p>{{ specialites.map(item => item.nom).join(' · ') || 'Réparateur professionnel' }}</p>
          <div><b>★ — <small>Avis clients</small></b><span>● {{ zones[0] || 'Zone non renseignée' }}</span><span>✓ Profil vérifié</span></div>
          <button class="profile-action" @click="demanderIntervention">Demander une intervention</button>
        </div>
      </section>
      <section class="detail-content">
        <div class="detail-main">
          <nav class="detail-tabs"><button :class="{ active: active === 'about' }" @click="active = 'about'">À propos</button><button :class="{ active: active === 'work' }" @click="active = 'work'">Réalisations</button><button :class="{ active: active === 'reviews' }" @click="active = 'reviews'">Avis clients</button></nav>
          <article v-if="active === 'about'" class="detail-box"><h2>Présentation</h2><p>{{ reparateur.description || 'Ce réparateur n’a pas encore ajouté de présentation.' }}</p><h3>Spécialités</h3><div class="detail-tags"><span v-for="item in specialites" :key="item.id">{{ item.nom }}</span><span v-if="!specialites.length">Non renseignées</span></div><h3>Zones d’intervention</h3><ul><li v-for="zone in zones" :key="zone">{{ zone }}</li><li v-if="!zones.length">Non renseignées</li></ul></article>
          <article v-else-if="active === 'work'" class="detail-box"><h2>Réalisations récentes</h2><p v-if="!realisations.length">Ce réparateur n’a pas encore publié de réalisation.</p><div v-else class="projects"><div v-for="item in realisations" :key="item.id"><div class="projet-images"><img v-if="item.photo_avant_url" :src="item.photo_avant_url" alt="Avant réparation"><span v-else>Avant non renseigné</span><img v-if="item.photo_apres_url" :src="item.photo_apres_url" alt="Après réparation"><span v-else>Après non renseigné</span></div><section><h3>{{ item.titre }}</h3><p>{{ item.description }}</p><b>{{ item.specialite_nom }}</b></section></div></div></article>
          <article v-else class="detail-box"><h2>Avis clients</h2><p>Aucun avis n’est encore disponible.</p></article>
        </div>
      </section>
    </template>
    <p v-else>Ce profil n’est pas disponible.</p>
  </main>
  <PiedDePage />
</template>

<style scoped>
.detail-image span{display:grid;place-items:center;width:100%;height:100%;background:#e7f5f1;color:#087f70;font-size:72px;font-weight:800}.profile-action{margin-top:20px;padding:12px 20px;border-radius:7px;background:#087f70;color:#fff;font-size:12px}.projet-images{display:grid;grid-template-columns:1fr 1fr;gap:4px;min-width:145px}.projet-images img,.projet-images span{width:100%;height:82px;border-radius:5px;object-fit:cover}.projet-images span{display:grid;place-items:center;background:#e7f5f1;color:#8093ae;font-size:9px;text-align:center}.projects>div{align-items:center}.projects b{display:inline-block;margin-top:6px;color:#087f70;font-size:10px}@media(max-width:600px){.projects>div{display:block}.projet-images{margin-bottom:12px}}
</style>
