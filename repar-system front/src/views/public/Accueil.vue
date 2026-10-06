<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import BarreRecherche from '../../components/public/BarreRecherche.vue'
import SectionUnivers from '../../components/public/SectionUnivers.vue'
import CarteReparateur from '../../components/public/CarteReparateur.vue'
import { chargerReparateursPublics } from '../../services/serviceReparateursPublics'
import imageBanniere2 from '../../assets/images/image copy 2.png'
import imageBanniere3 from '../../assets/images/image copy 3.png'
import imageBanniere4 from '../../assets/images/image.png'
import fondServices from '../../assets/images/reparateur poly.jpg.jpg'
import decorServices from '../../assets/images/unnamed.gif'

const videoAccueil = new URL('../../assets/images/Réparateur_répare_ordinateur_à_D…_20260929012113.mp4', import.meta.url).href

const categories = [
	{ label: 'Électricité', icon: 'bolt' },
	{ label: 'Plomberie', icon: 'water' },
	{ label: 'Électroménager', icon: 'appliance' },
	{ label: 'Climatisation', icon: 'climate' },
	{ label: 'Informatique', icon: 'computer' },
	{ label: 'Téléphonie', icon: 'smartphone' }
]
const imagesBanniere = [imageBanniere2, imageBanniere3, imageBanniere4]
const slideActif = ref(0)
const reparateurs = ref([])
const chargementReparateurs = ref(true)
let intervalId = null

onMounted(() => {
	intervalId = setInterval(() => {
		slideActif.value = (slideActif.value + 1) % imagesBanniere.length
	}, 3000)
	chargerReparateursPublics().then((data) => { reparateurs.value = data.slice(0, 5) }).catch(() => {}).finally(() => { chargementReparateurs.value = false })
})

onBeforeUnmount(() => {
	if (intervalId) clearInterval(intervalId)
})
</script>
<template><div class="home-page"><EntetePublic/></div><main><section class="hero"><video class="hero-video" :src="videoAccueil" autoplay muted loop playsinline preload="metadata" aria-label="Vidéo de réparation en arrière-plan"></video><div class="hero-video-overlay"><span class="hero-video-dot"></span> Réparation en direct</div><div class="hero-bg"></div><div class="hero-content"><h1>Trouvez le bon <em>réparateur</em><br>au bon prix près de<br>chez vous.</h1><p>Découvrez votre problème ou trouvez simplement un professionnel habile et vérifié près de chez vous en quelques clics.</p><BarreRecherche/></div></section><SectionUnivers/><section class="categories"><span class="eyebrow">NOS SERVICES</span><h2>Que souhaitez-vous réparer ?</h2><div class="category-grid"><div class="services-visual-card"><img :src="decorServices" alt="Effet visuel d’animation" /></div><div v-for="(cat, index) in categories" :key="cat.label" class="category" :style="{ '--delay': `${index * 0.22}s` }"><span class="category-icon"><AppIcon :name="cat.icon" :size="34"/></span><span class="category-label">{{cat.label}}</span></div></div></section><section class="featured-pros" aria-labelledby="featured-pros-title"><div class="featured-heading"><div><h2 id="featured-pros-title">À votre service.</h2></div></div><p v-if="chargementReparateurs" class="featured-state">Recherche des professionnels disponibles…</p><p v-else-if="!reparateurs.length" class="featured-state">Les profils vérifiés arrivent bientôt.</p><div v-else class="featured-grid"><CarteReparateur v-for="(reparateur, index) in reparateurs" :key="reparateur.id" :person="reparateur" :style="{ '--delay': `${index * 100}ms` }" /></div></section><RouterLink to="/reparateurs" class="featured-link featured-link-bottom">Voir tous les réparateurs <span>→</span></RouterLink></main><PiedDePage/></template>

<style scoped>
main {
	--home-title-content-gap: 80px;
	background: #f7fbfc;
}

main > section + section {
	margin-top: 28px;
}

.home-page :deep(.header){background:#0b1427;color:#fff;border-bottom-color:rgba(255,255,255,.12)}
.home-page :deep(.header a){color:#fff}
.home-page :deep(.header .logo-reparsystem){background:#fff;border-radius:8px;padding:3px}
.home-page :deep(.header .signup){background:#087f70;color:#fff}
.hero {
	position: relative;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 18px;
	background: #0b1427;
	min-height: 730px;
	padding: 34px 0 42px;
}

.hero-video {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
	filter: saturate(1.1) contrast(1.08);
}

.hero-bg {
	position: absolute;
	inset: 0;
	background: linear-gradient(90deg, rgba(6,29,47,.78) 0%, rgba(6,29,47,.58) 30%, rgba(6,29,47,.18) 60%, rgba(6,29,47,.06) 100%);
	z-index: 1;
	isolation: isolate;
}

@property --k {
	syntax: '<number>';
	initial-value: 0;
	inherits: false;
}

.hero-gallery {
	position: absolute;
	inset: -22% -8%;
	pointer-events: none;
	transform-style: preserve-3d;
	opacity: .7;
	filter: saturate(1.35) contrast(1.08);
	animation: hero-gallery-rotate 13s linear infinite, hero-gallery-progress 13s linear infinite;
}

.hero-gallery-image {
	--d: clamp(72px, 9vmin, 132px);
	--r: calc(6.5 * var(--d));
	--j: calc((var(--i) / var(--n)) + var(--k));
	--ca: calc(var(--j) * 1turn);
	position: absolute;
	top: 50%;
	left: 50%;
	grid-area: 1 / 1;
	width: var(--d);
	aspect-ratio: 1;
	object-fit: cover;
	border-radius: 50%;
	translate: calc(var(--r) * sin(var(--ca)) * pow(sin(.5 * var(--ca)), 4)) calc(-1 * var(--r) * cos(var(--ca))) calc(.25 * var(--r) * sin(var(--ca)));
	scale: calc(1 - 1.75 * abs(mod(var(--j), 1) - .5));
	box-shadow: 0 0 18px rgba(34, 211, 238, .48), 2px 2px 14px rgba(0, 0, 0, .5);
	animation: hero-gallery-rotate 13s linear infinite reverse, hero-gallery-progress 13s linear infinite;
}

.hero-gallery-image:nth-child(2n) {
	box-shadow: 0 0 22px rgba(251, 191, 36, .55), 2px 2px 14px rgba(0, 0, 0, .5);
}

.hero-gallery-image:nth-child(3n) {
	box-shadow: 0 0 22px rgba(52, 211, 153, .5), 2px 2px 14px rgba(0, 0, 0, .5);
}

@keyframes hero-gallery-progress {
	to { --k: 1; }
}

@keyframes hero-gallery-rotate {
	to { rotate: y 1turn; }
}

.hero-content {
	position: relative;
	z-index: 2;
	flex: 1;
	max-width: 760px;
	padding-left: 18px;
	margin-left: 0;
	padding-top: 120px;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	text-align: center;
	margin: 0 auto;
	padding-bottom: 24px;
}

.hero-video-overlay {
	position: absolute;
	left: 16px;
	bottom: 16px;
	display: inline-flex;
	align-items: center;
	gap: 8px;
	padding: 8px 12px;
	border: 1px solid rgba(255,255,255,0.22);
	border-radius: 999px;
	background: rgba(7, 17, 30, 0.52);
	backdrop-filter: blur(6px);
	color: #edf8ff;
	font-size: 11px;
	font-weight: 700;
	letter-spacing: 0.02em;
	z-index: 2;
}

.hero-video-dot {
	display: inline-block;
	width: 8px;
	height: 8px;
	border-radius: 50%;
	background: #5fe5c8;
	box-shadow: 0 0 0 4px rgba(95, 229, 200, 0.22);
}

.categories {
	position: relative;
	background: linear-gradient(180deg, rgba(0, 0, 0, 0.72), rgba(0, 0, 0, 0.72)), url('../../assets/images/reparateur poly.jpg.jpg') center/cover no-repeat;
	padding: 82px max(7%, 52px) 132px;
	isolation: isolate;
}

.services-visual-card {
	display: flex;
	align-items: center;
	justify-content: center;
	min-height: 220px;
	border-radius: 16px;
	overflow: hidden;
	animation: serviceGlow 5s ease-in-out infinite alternate;
	padding: 8px;
}

.services-visual-card img {
	width: clamp(170px, 16vw, 245px);
	height: auto;
	object-fit: contain;
	display: block;
	border-radius: 16px;
	filter: hue-rotate(105deg) saturate(1.7) brightness(1.22) contrast(1.08) drop-shadow(0 18px 30px rgba(8, 220, 190, 0.42));
}

@keyframes serviceGlow {
	0% {
		opacity: 0.88;
		transform: scale(1);
	}
	100% {
		opacity: 1;
		transform: scale(1.04);
	}
}

.categories > * {
	position: relative;
	z-index: 1;
}

.categories .eyebrow {
	font-size: 10px;
	letter-spacing: 1.4px;
	color: #76f5e4;
}

.categories h2 {
	margin: 16px 0 var(--home-title-content-gap);
	font-size: clamp(30px, 4vw, 48px);
	line-height: 1.12;
	letter-spacing: 0;
	color: #fff;
}

.category-grid {
	display: grid;
	grid-template-columns: repeat(7, minmax(0, 1fr));
	gap: 22px;
	max-width: 1320px;
	margin: 0 auto;
	align-items: stretch;
}

.services-visual-card {
	min-width: 0;
}

@media (max-width: 1180px) {
	.category-grid {
		grid-template-columns: repeat(3, minmax(0, 1fr));
	}
}

@media (max-width: 720px) {
	.category-grid {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
}

.category {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 18px;
	min-height: 200px;
	padding: 26px 18px 22px;
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 16px;
	background: rgba(255, 255, 255, 0.08);
	box-shadow: 0 14px 28px rgba(0, 0, 0, 0.18);
	backdrop-filter: blur(3px);
	animation: categoryFloat 7s ease-in-out infinite;
	animation-delay: var(--delay, 0s);
	transition: transform .2s ease, box-shadow .2s ease, background .2s ease;
}

@keyframes categoryFloat {
	0%, 100% {
		transform: translateY(0px);
		opacity: 0.96;
	}
	50% {
		transform: translateY(-8px);
		opacity: 1;
	}
}

.category:hover {
	transform: translateY(-4px);
	box-shadow: 0 18px 30px rgba(0, 0, 0, 0.22);
	background: rgba(255, 255, 255, 0.12);
}

.category-icon {
	display: grid;
	place-items: center;
	width: 74px;
	height: 74px;
	border-radius: 18px;
	background: rgba(138, 246, 224, 0.12);
	color: #76f5e4;
}

.category-icon svg {
	width: 34px;
	height: 34px;
}

.category-label {
	font-size: 15px;
	font-weight: 600;
	color: #f7fcff;
	text-align: center;
}

.featured-pros {
	padding: 72px max(2.5%, 30px) 36px;
	background: #f7fbfc;
}

.featured-heading {
	max-width: 1180px;
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	justify-content: space-between;
	gap: 30px;
	margin: 0 auto var(--home-title-content-gap);
}

.featured-heading > div { width: 100%; text-align: center; }

.featured-heading h2 {
	max-width: 570px;
	margin: 0 auto;
	color: #102a52;
	font-size: clamp(30px, 4vw, 48px);
	line-height: 1.05;
	letter-spacing: -.8px;
}

.featured-heading p {
	margin: 0;
	color: #75849a;
	font-size: 13px;
}

.featured-link {
	flex: none;
	position: static;
	display: inline-block;
	margin-top: 22px;
	padding: 12px 15px;
	border: 1px solid #c9e2df;
	border-radius: 8px;
	color: #087f70;
	background: #fff;
	font-size: 11px;
	font-weight: 800;
	transition: transform .2s ease, box-shadow .2s ease;
}

.featured-link:hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(8,127,112,.12); }
.featured-link span { margin-left: 8px; font-size: 16px; }
.featured-link.featured-link-bottom { display: flex; width: max-content; position: static; margin: 24px auto 16px; }
.featured-grid { max-width: 1640px; display: flex !important; flex-wrap: nowrap; gap: 28px; margin: 0 auto; overflow-x: auto; padding: 4px 2px 16px; scroll-snap-type: x mandatory; scrollbar-width: none; }
.featured-grid::-webkit-scrollbar { display: none; }
.featured-grid :deep(.pro-card) { flex: 0 0 max(230px, calc((100% - 112px) / 5)); min-width: 0; scroll-snap-align: start; border: 1px solid rgba(255, 255, 255, .88); background: rgba(255, 255, 255, .74); backdrop-filter: blur(18px) saturate(155%); box-shadow: 0 10px 28px rgba(20, 47, 82, .10), inset 0 1px 0 rgba(255, 255, 255, .95); transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.featured-grid :deep(.pro-card:hover) { transform: translateY(-6px); border-color: rgba(255, 255, 255, .98); box-shadow: 0 18px 38px rgba(20, 47, 82, .16), 0 0 0 1px rgba(255, 255, 255, .45), inset 0 1px 0 #fff; }
.featured-grid :deep(.photo) { height: 171px; }
.featured-grid :deep(.card-content) { padding: 14px 18px 17px; }
.featured-grid :deep(.name-score h3) { font-size: 15px; }
.featured-grid :deep(.name-score strong) { font-size: 11px; }
.featured-grid :deep(.company), .featured-grid :deep(.location) { font-size: 10px; }
.featured-grid :deep(.tags) { gap: 6px; margin-top: 16px; }
.featured-grid :deep(.tags span) { padding: 5px 7px; font-size: 7px; }
.featured-grid :deep(.profile-button) { height: 39px; margin-top: 16px; }
.featured-grid :deep(.pro-card) { opacity: 0; animation: featured-card-in .55s cubic-bezier(.2,.75,.25,1) var(--delay) forwards; }
.featured-state { max-width: 1180px; margin: 0 auto; padding: 28px; border: 1px dashed #cfe1e5; border-radius: 12px; color: #73879a; background: #fff; text-align: center; font-size: 12px; }
@keyframes featured-card-in { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 900px) {
	main { --home-title-content-gap: 64px; }
	main > section + section { margin-top: 18px; }
	.featured-grid { gap: 24px; }
	.featured-grid :deep(.pro-card) { flex-basis: 230px; }

	.hero {
		display: block;
		min-height: 560px;
	}

	.hero-content {
		padding: 0 24px;
		max-width: 100%;
		margin-left: 0;
	}

	.hero-gallery {
		inset: 0 -20%;
		opacity: .4;
		filter: saturate(1.2) contrast(1.04);
	}

	.hero-side-image-carousel {
		display: block;
		width: min(82vw, 480px);
		height: 380px;
		margin: 22px auto 0;
		border-radius: 18px;
	}

	.featured-heading { display: block; text-align: center; }
	.featured-link { position: static; }
}

@media (max-width: 600px) {
	main { --home-title-content-gap: 52px; }
	.categories h2 {
		font-size: 34px;
	}
	.featured-pros { padding: 56px 20px 36px; }
	.featured-grid { gap: 16px; }
	.featured-grid :deep(.pro-card) { flex-basis: min(76vw, 280px); }
	.featured-grid :deep(.photo) { height: 155px; }
}

.featured-link.featured-link-bottom { display: flex; width: max-content; margin: 24px auto 16px; }

</style>


