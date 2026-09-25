<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import BarreRecherche from '../../components/public/BarreRecherche.vue'
import SectionUnivers from '../../components/public/SectionUnivers.vue'
import SectionCommentCaMarche from '../../components/public/SectionCommentCaMarche.vue'
import CarteReparateur from '../../components/public/CarteReparateur.vue'
import { chargerReparateursPublics } from '../../services/serviceReparateursPublics'
import imageBanniere1 from '../../assets/images/image copy.png'
import imageBanniere2 from '../../assets/images/image copy 2.png'
import imageBanniere3 from '../../assets/images/image copy 3.png'
import imageBanniere4 from '../../assets/images/image.png'

const categories=[['ϟ','Électricité'],['♨','Plomberie'],['◉','Électroménager'],['≋','Climatisation'],['▱','Informatique'],['▯','Téléphonie']]
const imagesBanniere = [imageBanniere1, imageBanniere2, imageBanniere3, imageBanniere4]
const slideActif = ref(0)
const reparateurs = ref([])
const chargementReparateurs = ref(true)
let intervalId = null

onMounted(() => {
	intervalId = setInterval(() => {
		slideActif.value = (slideActif.value + 1) % imagesBanniere.length
	}, 3000)
	chargerReparateursPublics().then((data) => { reparateurs.value = data.slice(0, 6) }).catch(() => {}).finally(() => { chargementReparateurs.value = false })
})

onBeforeUnmount(() => {
	if (intervalId) clearInterval(intervalId)
})
</script>
<template><div class="home-page"><EntetePublic/></div><main><section class="hero"><div class="hero-bg"><div class="hero-gallery" aria-hidden="true"><img v-for="(image, index) in imagesBanniere" :key="`gallery-${image}`" :src="image" class="hero-gallery-image" :style="{ '--i': index, '--n': imagesBanniere.length }" alt="" /></div></div><div class="hero-side-image-carousel"><img v-for="(image, index) in imagesBanniere" :key="image" :src="image" :class="{ active: index === slideActif }" class="hero-side-image" alt="Réparateur en action" /></div><div class="hero-content"><h1>Trouvez le bon <em>réparateur</em><br>au bon prix près de<br>chez vous.</h1><p>Découvrez votre problème ou trouvez simplement un professionnel habile et vérifié près de chez vous en quelques clics.</p><BarreRecherche/></div></section><SectionUnivers/><section class="categories"><span class="eyebrow">NOS SERVICES</span><h2>Que souhaitez-vous réparer ?</h2><div class="category-grid"><div v-for="cat in categories" :key="cat[1]" class="category"><b>{{cat[0]}}</b><span>{{cat[1]}}</span></div></div></section><section class="featured-pros" aria-labelledby="featured-pros-title"><div class="featured-heading"><div><h2 id="featured-pros-title">À votre service.</h2></div><RouterLink to="/reparateurs" class="featured-link">Voir tous les réparateurs <span>→</span></RouterLink></div><p v-if="chargementReparateurs" class="featured-state">Recherche des professionnels disponibles…</p><p v-else-if="!reparateurs.length" class="featured-state">Les profils vérifiés arrivent bientôt.</p><div v-else class="featured-grid"><CarteReparateur v-for="(reparateur, index) in reparateurs" :key="reparateur.id" :person="reparateur" :style="{ '--delay': `${index * 100}ms` }" /></div></section><SectionCommentCaMarche/></main><PiedDePage/></template>

<style scoped>
main {
	background: #f7fbfc;
}

main > section + section {
	margin-top: 28px;
}

.home-page :deep(.header){background:#0b1427;color:#fff;border-bottom-color:rgba(255,255,255,.12)}
.home-page :deep(.header a){color:#fff}
.home-page :deep(.header .brand-mark){color:#fff}
.home-page :deep(.header .signup){background:#087f70;color:#fff}
.hero {
	position: relative;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 18px;
	background: #0b1427;
	min-height: 650px;
	padding: 34px 0 42px;
}

.hero-bg {
	position: absolute;
	inset: 0;
	background: linear-gradient(90deg, rgba(6,29,47,.75) 0%, rgba(6,29,47,.48) 28%, rgba(6,29,47,.12) 58%, rgba(6,29,47,.08) 100%);
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
	z-index: 1;
	flex: 1;
	max-width: 760px;
	padding-left: 18px;
	margin-left: 0;
	padding-top: 92px;
}

.hero-side-image-carousel {
	position: relative;
	z-index: 1;
	width: min(42vw, 560px);
	height: 500px;
	margin-right: max(2.5%, 28px);
	margin-left: auto;
	align-self: center;
	transform: translateY(6px);
	border-radius: 0 22px 22px 0;
	overflow: hidden;
	box-shadow: 0 18px 40px rgba(11, 21, 43, 0.18);
}

.hero-side-image {
	position: absolute;
	inset: 0;
	width: 100%;
	height: 100%;
	object-fit: cover;
	opacity: 0;
	transition: opacity 0.6s ease-in-out;
}

.hero-side-image.active {
	opacity: 1;
}

.categories {
	background: #edf3f8;
	padding: 82px max(7%, 52px) 132px;
}

.categories .eyebrow {
	font-size: 10px;
	letter-spacing: 1.2px;
}

.categories h2 {
	margin: 16px 0 56px;
	font-size: clamp(30px, 4vw, 48px);
	line-height: 1.12;
	letter-spacing: 0;
}

.featured-pros {
	padding: 112px max(7%, 52px) 126px;
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
	margin: 0 auto 34px;
}

.featured-heading > div { width: 100%; text-align: center; }

.featured-heading h2 {
	max-width: 570px;
	margin: 12px auto 9px;
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
	position: absolute;
	right: 0;
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
.featured-grid { max-width: 1180px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 0 auto; }
.featured-grid :deep(.pro-card) { opacity: 0; animation: featured-card-in .55s cubic-bezier(.2,.75,.25,1) var(--delay) forwards; }
.featured-state { max-width: 1180px; margin: 0 auto; padding: 28px; border: 1px dashed #cfe1e5; border-radius: 12px; color: #73879a; background: #fff; text-align: center; font-size: 12px; }
@keyframes featured-card-in { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 900px) {
	main > section + section { margin-top: 18px; }

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
		height: 320px;
		margin: 22px auto 0;
		border-radius: 18px;
	}

	.featured-heading { display: block; text-align: center; }
	.featured-link { position: static; display: inline-block; margin-top: 22px; }
	.featured-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
	.categories h2 {
		margin-bottom: 40px;
		font-size: 34px;
	}
	.featured-pros { padding: 76px 20px 82px; }
	.featured-grid { grid-template-columns: 1fr; gap: 16px; }
}

</style>


