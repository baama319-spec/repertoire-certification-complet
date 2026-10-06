<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { api } from '../../services/api'

const props = defineProps({
  professionals: { type: Array, default: () => [] },
  initialPosition: { type: Object, default: null },
  autoLocate: { type: Boolean, default: true },
})

const mapElement = ref(null)
const router = useRouter()
const map = ref(null)
const distanceMax = ref(20)
const toutesCategories = 'Toutes les catégories'
const toutesLesNotes = 0
const specialite = ref(toutesCategories)
const noteMinimale = ref(toutesLesNotes)
const categories = ref([])
const selectedId = ref(null)
const userPosition = ref(null)
const userMarker = ref(null)
const selectedRoute = ref(null)
const markers = new Map()

const points = computed(() => props.professionals.filter(item => item.lat !== null && item.lon !== null && Number.isFinite(item.lat) && Number.isFinite(item.lon)))
const distanceInKm = item => {
  const distance = Number(item.distanceKm)
  if (Number.isFinite(distance) && distance > 0) return distance
  if (!userPosition.value) return null
  const latitude1 = userPosition.value.latitude * Math.PI / 180
  const latitude2 = item.lat * Math.PI / 180
  const deltaLatitude = (item.lat - userPosition.value.latitude) * Math.PI / 180
  const deltaLongitude = (item.lon - userPosition.value.longitude) * Math.PI / 180
  const a = Math.sin(deltaLatitude / 2) ** 2 + Math.cos(latitude1) * Math.cos(latitude2) * Math.sin(deltaLongitude / 2) ** 2
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

const normaliserTexte = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLocaleLowerCase('fr')
const filtered = computed(() => points.value.filter((item) => {
  const specialitesItem = [item.specialty, ...(Array.isArray(item.tags) ? item.tags : [])]
    .flatMap(value => String(value || '').split(/[,;|]/))
    .map(normaliserTexte)
    .filter(Boolean)
  const matchesCategory = specialite.value === toutesCategories || specialitesItem.includes(normaliserTexte(specialite.value))
  const distance = distanceInKm(item)
  const matchesDistance = distance == null || distance <= distanceMax.value
  const note = Number(item.score)
  const matchesRating = noteMinimale.value === toutesLesNotes || (Number.isFinite(note) && note >= noteMinimale.value)
  return matchesCategory && matchesDistance && matchesRating
}))

const chargerCategories = async () => {
  try {
    const data = await api('/specialites/')
    const categoriesActives = (data.results || data)
      .filter(item => item.actif !== false && item.nom)
      .map(item => item.nom.trim())
    categories.value = [toutesCategories, ...new Map(categoriesActives.map(nom => [normaliserTexte(nom), nom])).values()]
  } catch (_) {
    // En mode hors-ligne, les spécialités connues des professionnels restent filtrables.
    const categoriesConnues = props.professionals
      .flatMap(item => [item.specialty, ...(Array.isArray(item.tags) ? item.tags : [])])
      .flatMap(value => String(value || '').split(/[,;|]/))
      .map(value => value.trim())
      .filter(Boolean)
    categories.value = [toutesCategories, ...new Map(categoriesConnues.map(nom => [normaliserTexte(nom), nom])).values()]
  }
  if (!categories.value.some(nom => normaliserTexte(nom) === normaliserTexte(specialite.value))) {
    specialite.value = toutesCategories
  }
}

const reinitialiserFiltres = () => {
  specialite.value = toutesCategories
  distanceMax.value = 20
  noteMinimale.value = toutesLesNotes
}

const distanceLabel = item => {
  const distance = distanceInKm(item)
  return distance == null ? 'Distance indisponible' : `${distance.toFixed(1)} km`
}

const drivingTimeLabel = item => {
  const distance = distanceInKm(item)
  if (distance == null) return 'Durée indisponible'
  const minutes = Math.max(1, Math.round((distance / 30) * 60))
  return minutes < 60 ? `${minutes} min en voiture` : `${Math.floor(minutes / 60)} h ${minutes % 60} min en voiture`
}

const creerPopupProfil = (item) => {
  const lien = document.createElement('a')
  const routeProfil = { name: 'profil-reparateur', params: { slug: item.slug || String(item.id) } }
  lien.className = 'repairer-popup-link'
  lien.href = router.resolve(routeProfil).href
  lien.setAttribute('aria-label', `Ouvrir le profil de ${item.name}`)
  lien.title = 'Cliquer pour voir le profil du réparateur'

  const nom = document.createElement('strong')
  nom.className = 'repairer-popup-name'
  nom.textContent = item.name || 'Réparateur'
  const specialiteLabel = document.createElement('span')
  specialiteLabel.textContent = item.specialty || 'Réparation'
  const distance = document.createElement('strong')
  distance.textContent = distanceLabel(item)
  const duree = document.createElement('span')
  duree.textContent = drivingTimeLabel(item)
  const coordonnees = document.createElement('small')
  coordonnees.textContent = `${item.lat.toFixed(6)}, ${item.lon.toFixed(6)}`
  const action = document.createElement('span')
  action.className = 'repairer-popup-action'
  action.textContent = 'Voir le profil'

  lien.append(nom, specialiteLabel, distance, duree, coordonnees, action)
  L.DomEvent.on(lien, 'click', (event) => {
    L.DomEvent.preventDefault(event)
    L.DomEvent.stopPropagation(event)
    router.push(routeProfil)
  })
  return lien
}

const selectProfessional = (item) => {
  selectedId.value = item.id
  const marker = markers.get(item.id)
  if (marker && map.value) {
    map.value.setView(marker.marker.getLatLng(), 11, { animate: true })
    marker.marker.openPopup()
    drawRoute(item)
  }
}

const drawRoute = (item) => {
  if (selectedRoute.value) selectedRoute.value.remove()
  if (!map.value || !userPosition.value) return
  selectedRoute.value = L.polyline([
    [userPosition.value.latitude, userPosition.value.longitude],
    [item.lat, item.lon],
  ], { color: '#d93636', weight: 3, opacity: .7, dashArray: '8 8' }).addTo(map.value)
  selectedRoute.value.bindTooltip(`${distanceLabel(item)} · ${drivingTimeLabel(item)}`, {
    permanent: true,
    direction: 'center',
    className: 'route-info-label',
    opacity: 1,
  }).openTooltip()
}

const drawMarkers = () => {
  markers.forEach(({ marker, pulse }) => { marker.remove(); pulse.remove() })
  markers.clear()
  filtered.value.forEach((item) => {
    const pulse = L.circleMarker([item.lat, item.lon], {
      radius: 13,
      color: '#087f70',
      weight: 2,
      fillColor: '#087f70',
      fillOpacity: 0,
      className: 'repairer-pulse',
      interactive: false,
    }).addTo(map.value)
    const marker = L.circleMarker([item.lat, item.lon], {
      radius: selectedId.value === item.id ? 11 : 8,
      color: '#ffffff',
      weight: 3,
      fillColor: '#087f70',
      fillOpacity: 1,
      className: 'repairer-point',
    }).addTo(map.value)
    marker.bindPopup(creerPopupProfil(item))
    marker.on('click', () => { selectedId.value = item.id; drawRoute(item) })
    markers.set(item.id, { marker, pulse })
  })
}

const setUserPosition = (latitude, longitude) => {
    userPosition.value = { latitude, longitude }
    if (userMarker.value) userMarker.value.remove()
    userMarker.value = L.circleMarker([latitude, longitude], {
      radius: 8,
      color: '#ffffff',
      weight: 3,
      fillColor: '#d93636',
      fillOpacity: 1,
      className: 'client-point',
    }).addTo(map.value)
    userMarker.value.bindPopup('<strong>Votre position</strong>')
    if (map.value) map.value.setView([latitude, longitude], 11)
}

const locateUser = () => {
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition((position) => {
    setUserPosition(position.coords.latitude, position.coords.longitude)
  })
}

onMounted(async () => {
  await nextTick()
  await chargerCategories()
  map.value = L.map(mapElement.value, { zoomControl: false, scrollWheelZoom: false }).setView([14.4974, -14.4524], 7)
  L.control.zoom({ position: 'bottomright' }).addTo(map.value)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 18,
  }).addTo(map.value)
  drawMarkers()
  if (props.initialPosition) setUserPosition(props.initialPosition.latitude, props.initialPosition.longitude)
  else if (props.autoLocate) locateUser()
})

watch([filtered, selectedId], () => {
  if (map.value) drawMarkers()
})

watch(() => props.initialPosition, (position) => {
  if (position && map.value) setUserPosition(position.latitude, position.longitude)
}, { deep: true })

onBeforeUnmount(() => {
  if (userMarker.value) userMarker.value.remove()
  if (selectedRoute.value) selectedRoute.value.remove()
  if (map.value) map.value.remove()
})
</script>

<template>
  <section class="proximity-section">
    <div class="proximity-heading">
      <div>
        <h2>Trouvez un réparateur près de chez vous</h2>
      </div>
      <button class="locate-button" type="button" @click="locateUser">Utiliser ma position</button>
    </div>

    <div class="proximity-layout">
      <aside class="proximity-filters">
        <h3>Filtres</h3>
        <button class="reset-filter" type="button" @click="reinitialiserFiltres">Réinitialiser</button>
        <label>Catégorie
          <select v-model="specialite">
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
        </label>
        <div class="rating-filter">
          <span class="rating-filter-title">Note minimale</span>
          <div class="rating-filter-stars" role="group" aria-label="Filtrer selon la note minimale">
            <button v-for="star in 5" :key="star" type="button" :class="{ selected: noteMinimale >= star }" :aria-label="`${star} étoile${star > 1 ? 's' : ''} minimum`" :aria-pressed="noteMinimale === star" @click="noteMinimale = noteMinimale === star ? toutesLesNotes : star"><AppIcon name="star" :size="19" :fill="noteMinimale >= star ? 'currentColor' : 'none'" /></button>
          </div>
          <small class="rating-filter-hint">{{ noteMinimale ? `${noteMinimale} étoile${noteMinimale > 1 ? 's' : ''} et plus` : 'Toutes les notes' }}</small>
        </div>
        <label>Distance maximale <strong>{{ distanceMax }} km</strong>
          <input v-model.number="distanceMax" type="range" min="1" max="20">
          <span class="range-labels"><small>1 km</small><small>20 km</small></span>
        </label>
        <p class="filter-note">{{ filtered.length }} professionnel{{ filtered.length > 1 ? 's' : '' }} localisé{{ filtered.length > 1 ? 's' : '' }}</p>
      </aside>

      <div ref="mapElement" class="senegal-map" aria-label="Carte des réparateurs au Sénégal"></div>

      <aside class="nearby-list">
        <div class="nearby-list-header"><strong>{{ filtered.length }} artisans trouvés</strong><span>Les plus proches</span></div>
        <button v-for="item in filtered.slice(0, 5)" :key="item.id" class="nearby-card" :class="{ active: selectedId === item.id }" type="button" @click="selectProfessional(item)">
          <img :src="item.image" :alt="item.name">
          <span class="nearby-info"><strong>{{ item.name }}</strong><small>{{ item.specialty }}</small><span class="rating"><template v-if="item.score !== '—'"><AppIcon name="star" :size="12" fill="currentColor" /> {{ item.score }}</template><template v-else>Aucun avis</template> <em>·</em> {{ distanceLabel(item) }}</span></span>
          <span class="nearby-actions"><RouterLink v-if="item.slug" class="profile-link" :to="`/reparateurs/${item.slug}`" @click.stop>Voir le profil</RouterLink></span>
        </button>
        <p v-if="!filtered.length" class="empty-map">Aucun réparateur dans ces critères.</p>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.proximity-section { padding: 70px max(5%, 48px) 82px; background: linear-gradient(180deg, #f2f7fa 0%, #eef3f7 100%); }
.proximity-heading { max-width: 1240px; margin: 0 auto 25px; display: flex; align-items: end; justify-content: space-between; gap: 20px; }
.proximity-eyebrow { color: #087f70; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
.proximity-heading h2 { margin: 8px 0 7px; color: #123f45; font-size: clamp(22px, 3vw, 32px); }
.proximity-heading p { margin: 0; color: #758195; font-size: 13px; }
.locate-button { padding: 12px 16px; border: 1px solid #d6e5e1; border-radius: 10px; color: #087f70; background: #fff; font-size: 11px; box-shadow: 0 10px 22px rgba(8, 127, 112, 0.08); transition: all .2s ease; }
.locate-button:hover { transform: translateY(-1px); box-shadow: 0 12px 26px rgba(8, 127, 112, 0.12); }
.proximity-layout { max-width: 1240px; min-height: 530px; margin: auto; display: grid; grid-template-columns: 195px minmax(400px, 1fr) 285px; overflow: hidden; border: 1px solid #e5ebf2; border-radius: 18px; background: #fff; box-shadow: 0 18px 45px rgba(21, 45, 62, 0.08); }
.proximity-filters { padding: 22px 18px; border-right: 1px solid #e8edf2; color: #536175; font-size: 11px; background: linear-gradient(180deg, #fdfefe 0%, #f6fafb 100%); }
.proximity-filters h3 { margin: 0 0 18px; color: #152743; font-size: 14px; }
.reset-filter { float: right; margin-top: -35px; padding: 0; background: none; color: #087f70; font-size: 9px; }
.proximity-filters label { display: block; margin: 22px 0; font-weight: 700; }
.proximity-filters select { display: block; width: 100%; margin-top: 8px; padding: 10px 10px; border: 1px solid #dfe7ee; border-radius: 8px; color: #667489; background: #fff; font-size: 10px; }
.rating-filter { margin: 22px 0; }
.rating-filter-title { display: block; color: #536175; font-weight: 700; }
.rating-filter-stars { display: flex; gap: 4px; margin-top: 8px; }
.rating-filter-stars button { padding: 2px; background: transparent; color: #cbd3dd; font-size: 23px; line-height: 1; transition: color .15s ease, transform .15s ease; }
.rating-filter-stars button:hover { color: #f0b429; transform: scale(1.12); }
.rating-filter-stars button.selected { color: #f0b429; }
.rating-filter-hint { display: block; margin-top: 5px; color: #8190a3; font-size: 9px; font-weight: 400; }
.proximity-filters strong { float: right; color: #087f70; font-size: 10px; }
.proximity-filters input { width: 100%; margin-top: 13px; accent-color: #087f70; }
.range-labels { display: flex; justify-content: space-between; color: #9da8b6; font-weight: 400; }
.availability-row { display: flex; align-items: center; justify-content: space-between; gap: 5px; font-weight: 700; }
.status-dot { width: 22px; height: 13px; border-radius: 20px; background: #159b78; position: relative; }
.status-dot::after { content: ''; position: absolute; width: 9px; height: 9px; right: 2px; top: 2px; border-radius: 50%; background: #fff; }
.filter-note { margin-top: 32px; color: #087f70; font-size: 10px; }
.senegal-map { min-height: 530px; background: #d7edf2; z-index: 0; border-left: 1px solid #edf3f7; border-right: 1px solid #edf3f7; }
.senegal-map :deep(.repairer-popup-link) { display: grid; gap: 3px; min-width: 150px; color: #152743; text-decoration: none; cursor: pointer; }
.senegal-map :deep(.repairer-popup-link:hover .repairer-popup-name), .senegal-map :deep(.repairer-popup-action) { color: #087f70; }
.senegal-map :deep(.repairer-popup-action) { margin-top: 5px; font-size: 11px; font-weight: 800; }
.senegal-map :deep(.route-info-label) { border: 0; border-radius: 6px; padding: 6px 9px; color: #7d2525; background: #fff; box-shadow: 0 3px 10px #61202026; font-size: 11px; font-weight: 800; white-space: nowrap; }
.senegal-map :deep(.route-info-label::before) { display: none; }
:deep(.repairer-pulse) { transform-box: fill-box; transform-origin: center; animation: repairer-radius-pulse 1.8s ease-out infinite; }
:deep(.repairer-point) { filter: drop-shadow(0 1px 3px #087f7066); }
@keyframes repairer-radius-pulse { 0% { opacity: .85; transform: scale(.7); } 70%, 100% { opacity: 0; transform: scale(1.9); } }
:deep(.client-point) { filter: drop-shadow(0 1px 3px #d9363666); }
.nearby-list { padding: 18px 12px; overflow: auto; background: linear-gradient(180deg, #f9fcfd 0%, #f4f8fb 100%); }
.nearby-list-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; color: #152743; font-size: 12px; }
.nearby-list-header span { color: #758195; font-size: 9px; }
.nearby-card { width: 100%; display: flex; align-items: center; gap: 8px; padding: 11px 10px; margin-bottom: 10px; border: 1px solid #edf1f5; border-radius: 12px; background: #fff; text-align: left; box-shadow: 0 6px 16px rgba(17, 40, 64, 0.04); transition: all .2s ease; }
.nearby-card:hover { transform: translateY(-1px); box-shadow: 0 10px 22px rgba(17, 40, 64, 0.08); }
.nearby-card.active { background: linear-gradient(180deg, #f0faf8 0%, #e8f7f4 100%); border-color: #cfece7; }
.nearby-card img { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; }
.nearby-info { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 3px; }
.nearby-info strong { overflow: hidden; color: #152743; font-size: 10px; text-overflow: ellipsis; white-space: nowrap; }
.nearby-info small { color: #7e8a9b; font-size: 8px; }
.rating { color: #ec9d16; font-size: 8px; }
.rating em { color: #b4bdc8; font-style: normal; }
.empty-map { color: #758195; font-size: 11px; line-height: 1.5; }
@media (max-width: 980px) { .proximity-layout { grid-template-columns: 170px 1fr; } .nearby-list { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(2, 1fr); gap: 0 12px; } .nearby-list-header { grid-column: 1 / -1; } }
@media (max-width: 650px) { .proximity-section { padding: 45px 16px 55px; } .proximity-heading { display: block; } .locate-button { margin-top: 16px; } .proximity-layout { display: block; } .proximity-filters { border-right: 0; border-bottom: 1px solid #e8edf2; } .senegal-map { min-height: 380px; } .nearby-list { display: block; } }
</style>
