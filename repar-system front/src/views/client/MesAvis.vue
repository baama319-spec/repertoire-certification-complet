<template>
	<div class="page">
		<EnteteClient />
		<main>
			<span>MON COMPTE</span>
			<h1>Mes avis</h1>
			<p>Retrouvez les évaluations transmises aux réparateurs après vos demandes acceptées.</p>
			<p v-if="loading" class="message">Chargement de vos avis…</p>
			<div v-else-if="error" class="message error" role="alert"><p>{{ error }}</p><button type="button" @click="charger">Réessayer</button></div>
			<article v-else-if="!reviews.length" class="empty"><b>Pas encore d’avis</b><small>Après l’acceptation d’une demande, ouvrez son détail pour noter le réparateur.</small><RouterLink to="/client/demandes">Voir mes demandes</RouterLink></article>
			<section v-else class="reviews" aria-label="Avis envoyés">
				<article v-for="item in reviews" :key="item.id" class="review">
					<header><div><strong>{{ item.demande_appareil || 'Demande de réparation' }}</strong><small>{{ item.demande_specialite || 'Réparation générale' }} · Demande #{{ item.demande }}</small></div><time>{{ item.date }}</time></header>
					<p class="rating"><span><AppIcon v-for="star in 5" :key="star" name="star" :size="15" :fill="star <= item.note ? 'currentColor' : 'none'" /></span>　{{ item.note }}/5</p>
					<p v-if="item.commentaire" class="comment">“{{ item.commentaire }}”</p>
					<p class="pro">Réparateur : <b>{{ item.reparateur_nom || 'Réparateur' }}</b></p>
				</article>
			</section>
			<RouterLink v-if="reviews.length" class="requests-link" to="/client/demandes">Retour à mes demandes</RouterLink>
		</main>
	</div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import EnteteClient from '../../components/client/EnteteClient.vue'
import { chargerAvis } from '../../services/serviceAvis'

const reviews = ref([])
const loading = ref(true)
const error = ref('')

const charger = async () => {
	loading.value = true
	error.value = ''
	try {
		reviews.value = (await chargerAvis()).map(avis => ({
			...avis,
			note: Number(avis.note),
			date: avis.date_creation ? new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long' }).format(new Date(avis.date_creation)) : 'Date indisponible',
		}))
	} catch (requestError) {
		error.value = requestError.message
	} finally {
		loading.value = false
	}
}

onMounted(charger)
</script>
<style scoped>
.page{min-height:100vh;padding:25px;background:#f4f8fc;color:#12376c}.page>:first-child{margin-left:auto;width:max-content}main{max-width:880px;margin:55px auto}main>span{font-size:11px;color:#087f70;font-weight:800;letter-spacing:.7px}h1{margin:10px 0;font-size:34px}main>p{color:#6380aa;line-height:1.6}.message,.empty{margin-top:28px;padding:30px;border:1px solid #dce8f3;border-radius:12px;background:#fff;text-align:center;color:#6380aa}.error{color:#a52e3a}.message button{padding:10px 15px;border:0;border-radius:7px;background:#087f70;color:#fff;cursor:pointer}.empty{display:grid;gap:14px}.empty b{font-size:19px;color:#12376c}.empty a,.requests-link{color:#087f70;font-weight:700}.reviews{display:grid;gap:14px;margin-top:28px}.review{padding:20px;border:1px solid #dce8f3;border-radius:12px;background:#fff;box-shadow:0 4px 14px #163e6808}.review header{display:flex;justify-content:space-between;gap:14px}.review header div{display:grid;gap:6px}.review header strong{color:#12376c}.review small,.review time,.pro{color:#6380aa;font-size:12px}.rating{margin:14px 0;color:#5374a4;font-size:13px}.rating span{color:#f2ad20;font-size:19px;letter-spacing:2px}.comment{margin:0;padding:13px;border-radius:8px;background:#f5f8fc;color:#405d82;line-height:1.6}.pro{margin-bottom:0}.pro b{color:#23466f}.requests-link{display:inline-block;margin-top:20px}
</style>
