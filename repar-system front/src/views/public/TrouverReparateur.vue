<script setup>
import { computed, onMounted, ref } from 'vue'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import CarteReparateur from '../../components/public/CarteReparateur.vue'
import CarteProximite from '../../components/public/CarteProximite.vue'
import { chargerReparateursPublics } from '../../services/serviceReparateursPublics'
const reparateurs = ref([])
const recherche = ref('')
const chargement = ref(true)
const erreur = ref('')
const visibles = computed(() => {
	const terme = recherche.value.trim().toLowerCase()
	return !terme ? reparateurs.value : reparateurs.value.filter(p => [p.name, p.specialty, p.location, ...p.tags].join(' ').toLowerCase().includes(terme))
})
const charger = (coordonnees = {}) => chargerReparateursPublics(coordonnees).then(data => { reparateurs.value = data })
onMounted(() => {
	if (!navigator.geolocation) {
		charger().catch(e => { erreur.value = e.message }).finally(() => { chargement.value = false })
		return
	}
	navigator.geolocation.getCurrentPosition(
		position => charger({ latitude: position.coords.latitude, longitude: position.coords.longitude }).catch(e => { erreur.value = e.message }).finally(() => { chargement.value = false }),
		() => charger().catch(e => { erreur.value = e.message }).finally(() => { chargement.value = false }),
		{ enableHighAccuracy: true, timeout: 8000 }
	)
})
</script>
<template>
	<EntetePublic />
	<main>
		<section class="search-hero"><h1>Quel professionnel recherchez-vous ?</h1><form class="wide-search" @submit.prevent><label>⌕ <input v-model.trim="recherche" placeholder="Spécialité, service ou zone..."></label><button>Rechercher</button></form></section>
		<CarteProximite :professionals="reparateurs" />
		<section class="results"><div class="results-head"><h2>{{ visibles.length }} réparateur{{ visibles.length > 1 ? 's' : '' }} trouvé{{ visibles.length > 1 ? 's' : '' }}</h2></div><p v-if="chargement">Chargement des réparateurs…</p><p v-else-if="erreur">{{ erreur }}</p><p v-else-if="!visibles.length">Aucun réparateur ne correspond à votre recherche.</p><div v-else class="pro-grid result-grid"><CarteReparateur v-for="p in visibles" :key="p.id" :person="p" search /></div></section>
	</main>
	<PiedDePage />
</template>

<style scoped>
.results {
	background: #edf3f8;
}
</style>
