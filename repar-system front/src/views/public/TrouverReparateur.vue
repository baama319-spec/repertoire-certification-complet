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
		<section class="results"><div class="results-head"><h2>{{ visibles.length }} réparateur{{ visibles.length > 1 ? 's' : '' }} trouvé{{ visibles.length > 1 ? 's' : '' }}</h2></div><p v-if="chargement">Chargement des réparateurs…</p><p v-else-if="erreur">{{ erreur }}</p><p v-else-if="!visibles.length">Aucun réparateur ne correspond à votre recherche.</p><div v-else class="pro-grid result-grid"><CarteReparateur v-for="p in visibles" :key="p.id" :person="p" search /></div></section>
		<CarteProximite :professionals="reparateurs" />
	</main>
	<PiedDePage />
</template>

<style scoped>
.wide-search label {
	display: flex;
	align-items: center;
	min-height: 48px;
	border: 1px solid #c8d8df;
	background: #fff;
	color: #087f70;
	font-size: 19px;
	box-shadow: inset 0 1px 3px rgba(16, 42, 82, .06);
}
.wide-search input {
	min-height: 44px;
	color: #173b4a;
	font-size: 14px;
	font-weight: 500;
}
.wide-search input::placeholder {
	color: #526a78;
	font-size: 13px;
	font-weight: 500;
	opacity: 1;
}
.wide-search label:focus-within {
	border-color: #087f70;
	box-shadow: 0 0 0 3px rgba(8, 127, 112, .14);
}
.results {
	background: #edf3f8;
}
</style>
