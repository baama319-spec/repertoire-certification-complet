<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import BarreRecherche from '../../components/public/BarreRecherche.vue'
import SectionUnivers from '../../components/public/SectionUnivers.vue'
import CarteReparateur from '../../components/public/CarteReparateur.vue'
import { chargerReparateursPublics } from '../../services/serviceReparateursPublics'
import imageBanniere2 from '../../assets/images/image copy 2.png'
import imageBanniere3 from '../../assets/images/image copy 3.png'
import imageBanniere4 from '../../assets/images/image.png'
import fondServices from '../../assets/images/image copy 6.png'
import imageAtelierAuto from '../../assets/images/image copy 2.png'
import imageAtelierPlomberie from '../../assets/images/image copy 3.png'
import imageAtelierElectronique from '../../assets/images/image copy 5.png'
import imageAtelierInformatique from '../../assets/images/clim repair 1.jpg'

const videoAccueil = new URL('../../assets/images/Réparateur_répare_ordinateur_à_D…_20260929012113.mp4', import.meta.url).href
const grilleReparateurs = ref(null)
const pauseDefilement = ref(false)
let defilementInterval = null

const demarrerDefilement = async () => {
	await nextTick()
	if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
	const grille = grilleReparateurs.value
	if (!grille) return
	grille.scrollLeft = grille.scrollWidth - grille.clientWidth
	defilementInterval = window.setInterval(() => {
		const grille = grilleReparateurs.value
		if (!grille || pauseDefilement.value || document.visibilityState !== 'visible') return
		const carte = grille.firstElementChild
		if (!carte) return
		const styles = window.getComputedStyle(grille)
		const pas = carte.getBoundingClientRect().width + (parseFloat(styles.columnGap) || 0)
		const debut = grille.scrollLeft <= 2
		grille.scrollTo({ left: debut ? grille.scrollWidth - grille.clientWidth : grille.scrollLeft - pas, behavior: 'smooth' })
	}, 3200)
}

onMounted(() => {
	intervalId = setInterval(() => {
		slideActif.value = (slideActif.value + 1) % imagesBanniere.length
	}, 3000)
	chargerReparateursPublics().then((data) => {
		reparateurs.value = data
	}).catch(() => {
	}).finally(() => {
		chargementReparateurs.value = false
		if (reparateurs.value.length) demarrerDefilement()
	})
})

onBeforeUnmount(() => {
	if (intervalId) clearInterval(intervalId)
	if (defilementInterval) clearInterval(defilementInterval)
})

const categories = [
	{ label: 'Électricité', icon: 'bolt' },
	{ label: 'Plomberie', icon: 'water' },
	{ label: 'Électroménager', icon: 'appliance' },
	{ label: 'Climatisation', icon: 'climate' },
	{ label: 'Informatique', icon: 'computer' },
	{ label: 'Téléphonie', icon: 'smartphone' }
]
const imagesBanniere = [imageBanniere2, imageBanniere3, imageBanniere4]
const imagesReparation = [
	{ src: imageAtelierAuto, alt: 'Réparatrice intervenant sur un véhicule' },
	{ src: fondServices, alt: 'Réparateur intervenant dans une cuisine' },
	{ src: imageAtelierPlomberie, alt: 'Technicien réparant un équipement de plomberie' },
	{ src: imageAtelierElectronique, alt: 'Technicien réparant un appareil électronique' },
	{ src: imageAtelierInformatique, alt: 'Réparateur intervenant sur un ordinateur' },
]
const slideActif = ref(0)
const reparateurs = ref([])
const chargementReparateurs = ref(true)
let intervalId = null
</script>

<template>
  <div class="home-page"><EntetePublic /></div>
  <main>
    <section class="hero">
      <video class="hero-video" :src="videoAccueil" autoplay muted loop playsinline preload="metadata" aria-label="Vidéo de réparation en arrière-plan"></video>
      <div class="hero-video-overlay"><span class="hero-video-dot"></span> Réparation en direct</div>
      <div class="hero-bg"></div>
      <div class="hero-content">
        <h1>Trouvez le bon <em>réparateur</em><br>au bon prix près de<br>chez vous.</h1>
        <p>Découvrez votre problème ou trouvez simplement un professionnel habile et vérifié près de chez vous en quelques clics.</p>
        <BarreRecherche />
      </div>
    </section>
    <SectionUnivers />
    <section class="how-it-works" aria-labelledby="how-it-works-title">
			<h2 id="how-it-works-title" class="how-it-works-title">Comment ça <em>marche</em></h2>
      <div class="how-it-works-inner">
        <div class="how-it-works-visual" aria-label="Photos de différents métiers de réparation">
          <img v-for="photo in imagesReparation.slice(0, 4)" :key="photo.src" :src="photo.src" :alt="photo.alt" loading="lazy" decoding="async" />
        </div>
        <div class="how-it-works-copy">
          <ol class="steps-list">
            <li class="step-item">
              <span class="step-number">01</span>
              <div class="step-content">
                <h3>Décrivez votre problème</h3>
                <p>Indiquez l’appareil et la panne. Ajoutez une photo si besoin.</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">02</span>
              <div class="step-content">
                <h3>Analyse rapide</h3>
                <p>Notre système donne une première idée du problème et de son urgence.</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">03</span>
              <div class="step-content">
                <h3>Trouvez un réparateur</h3>
                <p>Comparez les profils, spécialités, avis et proches de chez vous.</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">04</span>
              <div class="step-content">
                <h3>Choisissez</h3>
                <p>Consultez le profil et les réalisations avant de faire votre choix.</p>
              </div>
            </li>
            <li class="step-item">
              <span class="step-number">05</span>
              <div class="step-content">
                <h3>Suivez la réparation</h3>
                <p>Suivez l’évolution jusqu’à la finalisation de l’intervention.</p>
              </div>
            </li>
          </ol>
        </div>
      </div>
    </section>
		<section class="categories">
			<span class="eyebrow">NOS SERVICES</span>
			<h2>Que souhaitez-vous réparer ?</h2>
			<div class="category-grid">
				<div v-for="(cat, index) in categories" :key="cat.label" class="category" :style="{ '--delay': `${index * 0.22}s` }">
					<span class="category-icon"><AppIcon :name="cat.icon" :size="34" /></span>
					<span class="category-label">{{ cat.label }}</span>
				</div>
			</div>
		</section>
    <section class="featured-pros" aria-labelledby="featured-pros-title">
      <div class="featured-heading"><div><h2 id="featured-pros-title">À votre <em>service</em></h2></div></div>
      <p v-if="chargementReparateurs" class="featured-state">Recherche des professionnels disponibles…</p>
      <p v-else-if="!reparateurs.length" class="featured-state">Les profils vérifiés arrivent bientôt.</p>
	<div v-else ref="grilleReparateurs" class="featured-grid" @mouseenter="pauseDefilement = true" @mouseleave="pauseDefilement = false" @focusin="pauseDefilement = true" @focusout="pauseDefilement = false">
        <CarteReparateur v-for="(reparateur, index) in reparateurs.slice(0, 6)" :key="reparateur.id" :person="reparateur" :style="{ '--delay': `${index * 100}ms` }" />
      </div>
    </section>
  </main>
  <PiedDePage />
</template>

<style scoped>
main {
	--home-title-content-gap: 30px;
	background: #f7fbfc;
}

main > section + section {
	margin-top: 48px;
}

.home-page :deep(.header){background:#111827;color:#fff;border-bottom-color:rgba(255,255,255,.16)}
.home-page :deep(.header a){color:#fff}
.home-page :deep(.header .logo-reparsystem){background:#fff;border-radius:8px;padding:3px}
.home-page :deep(.header .signup){background:#087f70;color:#fff}
.home-page + main + :deep(.footer){background-color:#111827}
.hero {
	position: relative;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 18px;
	background: #111827;
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
	background: #111827;
}

.hero-bg {
	position: absolute;
	inset: 0;
	background: linear-gradient(90deg, rgba(17,24,39,.58) 0%, rgba(17,24,39,.38) 30%, rgba(17,24,39,.12) 60%, transparent 100%);
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
	padding: 110px max(7%, 52px) 160px;
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
	margin: 18px 0 42px;
	font-size: clamp(30px, 4vw, 52px);
	line-height: 1.08;
	letter-spacing: 0;
	color: #fff;
}

.category-grid {
	display: grid;
	grid-template-columns: repeat(6, minmax(180px, 1fr));
	gap: 26px;
	max-width: 1320px;
	margin: 0 auto;
	align-items: stretch;
	justify-content: center;
	justify-items: center;
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
	width: 100%;
	max-width: 220px;
	min-height: 220px;
	padding: 28px 20px 24px;
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
	color: #fff;
}

.category-icon svg {
	width: 34px;
	height: 34px;
	stroke: #fff;
	fill: none;
}

.category-label {
	font-size: 15px;
	font-weight: 600;
	color: #f7fcff;
	text-align: center;
}

.featured-pros {
	padding: 48px max(2.5%, 30px) 140px;
	background: #f7fbfc;
}

main > .featured-pros {
	margin-top: 28px;
}

.featured-heading {
	max-width: 1180px;
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 30px;
	margin: 0 auto 72px;
}

.featured-heading > div { width: 100%; text-align: center; }

.featured-heading h2 {
	max-width: 700px;
	margin: 0 auto;
	color: #102a52;
	font-size: clamp(30px, 3vw, 44px);
	line-height: 1.05;
	letter-spacing: -.8px;
}

.featured-heading h2 em {
	color: #0a7d73;
	font-style: normal;
}

.featured-state {
	max-width: 1180px;
	margin: 0 auto 28px;
	text-align: center;
	color: #5d6f7a;
	font-size: 13px;
}

.featured-grid {
	max-width: 1280px;
	display: flex;
	justify-content: flex-start;
	align-items: stretch;
	gap: 22px;
	margin: 0 auto;
	padding: 2px 0 8px;
	overflow-x: auto;
	overflow-y: hidden;
	scroll-snap-type: x mandatory;
	scrollbar-width: none;
	overscroll-behavior-x: contain;
}

.featured-grid::-webkit-scrollbar {
	display: none;
}

.featured-grid :deep(.pro-card) {
	position: relative;
	isolation: isolate;
	width: 220px;
	flex: 0 0 220px;
	scroll-snap-align: start;
	min-width: 0;
	padding: 0;
	border: 1px solid #d2e2e4;
	border-radius: 12px;
	background: #fff;
	box-shadow: none;
	transition: translate .28s ease, border-color .28s ease;
	box-sizing: border-box;
}

.featured-grid :deep(.pro-card::before) {
	content: '';
	position: absolute;
	z-index: 2;
	inset: 0;
	border-radius: inherit;
	background: linear-gradient(110deg, transparent 20%, rgba(255, 255, 255, .42) 48%, transparent 72%);
	transform: translateX(-120%);
	pointer-events: none;
}

.featured-grid :deep(.pro-card:hover) {
	translate: 0 -5px;
	border-color: #b9d9d3;
	box-shadow: none;
}

.featured-grid :deep(.pro-card:hover::before) {
	animation: featured-card-shine .75s ease forwards;
}

.featured-grid :deep(.photo) {
	height: 118px;
	border-radius: 10px 10px 0 0;
	background-size: cover;
	transition: filter .3s ease;
}

.featured-grid :deep(.pro-card:hover .photo) {
	filter: saturate(1.06);
}

.featured-grid :deep(.badge) { font-size: 9px; }
.featured-grid :deep(.card-content) { padding: 10px 10px 8px; }
.featured-grid :deep(.name-score h3) { font-size: 14px; margin: 0; }
.featured-grid :deep(.name-score strong) { font-size: 11px; }
.featured-grid :deep(.rating svg) { color: #f2ae16; width: 12px; height: 12px; }
.featured-grid :deep(.company) { display: none; }
.featured-grid :deep(.location) { margin-top: 7px; font-size: 10px; }
.featured-grid :deep(.location svg) { color: var(--rs-primary, #087f70); stroke-width: 2.5; width: 12px; height: 12px; }
.featured-grid :deep(.tags) { gap: 5px; margin-top: 8px; }
.featured-grid :deep(.tags span) { display: inline-flex; align-items: center; gap: 5px; border: 1px solid #d9e3e5; border-radius: 999px; background: #fff; color: var(--rs-ink, #123f45); padding: 4px 7px; font-size: 8px; }
.featured-grid :deep(.tags span svg) { color: var(--rs-primary, #087f70); stroke-width: 2.3; width: 10px; height: 10px; }
.featured-grid :deep(.profile-button) { border-color: #d8e0e3; background: #fff; color: #34454b; font-size: 10px; padding: 7px 8px; }
.featured-grid :deep(.profile-button:hover) { border-color: #c7d0d3; background: #f3f5f5; color: #25363c; }

.how-it-works {
	padding: 18px 0 72px;
	background: #f7fbfc;
}

.how-it-works-title {
	max-width: 1180px;
	margin: 0 auto 48px;
	color: #123f45;
	font-size: clamp(30px, 3vw, 48px);
	font-weight: 800;
	line-height: 1.12;
	letter-spacing: -.8px;
	text-align: center;
}

.how-it-works-title em {
	color: #087f70;
	font-style: normal;
}

.how-it-works-inner {
	display: grid;
	grid-template-columns: minmax(0, 1.06fr) minmax(0, .94fr);
	align-items: center;
	gap: -2px;
	max-width: 1180px;
	margin: 0 auto;
	padding: 0;
}

.how-it-works-visual {
	position: relative;
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	grid-template-rows: repeat(2, minmax(0, 1fr));
	gap: 12px;
	overflow: hidden;
	width: 100%;
	height: 520px;
	margin: 0;
	padding: 4px;
}

.how-it-works-visual img {
	display: block;
	width: 100%;
	height: 100%;
	object-fit: cover;
	border-radius: 18px;
	box-shadow: 0 18px 30px rgba(17, 24, 39, 0.10);
	transform-origin: center center;
	animation: image-float 8s ease-in-out infinite alternate;
	transition: transform 0.35s ease, box-shadow 0.35s ease;
}

.how-it-works-visual img:hover {
	transform: translateY(-4px) scale(1.02);
	box-shadow: 0 22px 36px rgba(17, 24, 39, 0.14);
}

.how-it-works-visual img:nth-child(1) { grid-column: 1; grid-row: 1; animation-delay: 0s; }
.how-it-works-visual img:nth-child(2) { grid-column: 1; grid-row: 2; animation-delay: .5s; }
.how-it-works-visual img:nth-child(3) { grid-column: 2; grid-row: 1 / span 2; animation-delay: 1s; }
.how-it-works-visual img:nth-child(4) { grid-column: 3; grid-row: 1; animation-delay: 1.5s; }
.how-it-works-visual img:nth-child(5) {
  grid-column: 4;
  grid-row: 1 / span 2;
  animation-delay: 2s;
  object-fit: cover;
  object-position: center;
}

@keyframes image-float {
	0% {
		transform: translateY(0px) scale(1);
	}
	50% {
		transform: translateY(-6px) scale(1.02);
	}
	100% {
		transform: translateY(0px) scale(1);
	}
}

.how-it-works-copy {
	padding: 0;
}

.steps-list {
	list-style: none;
	display: grid;
	gap: 12px;
	padding: 0;
	margin: 0;
}

.step-item {
	display: grid;
	grid-template-columns: 52px minmax(0, 1fr);
	gap: 12px;
	align-items: center;
	padding: 14px 14px 13px;
	border: 1px solid rgba(16, 42, 82, 0.08);
	border-radius: 16px;
	background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(239,249,247,0.92));
	box-shadow: 0 10px 22px rgba(17, 24, 39, 0.04);
	opacity: 0;
	transform: translateY(14px);
	animation: step-entry .55s ease forwards;
}

.step-item:nth-child(1) { animation-delay: .08s; }
.step-item:nth-child(2) { animation-delay: .16s; }
.step-item:nth-child(3) { animation-delay: .24s; }
.step-item:nth-child(4) { animation-delay: .32s; }
.step-item:nth-child(5) { animation-delay: .40s; }

@keyframes step-entry {
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

.step-number {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 52px;
	height: 52px;
	border-radius: 14px;
	background: linear-gradient(135deg, #0a7f73, #5cd7c5);
	color: #fff;
	font-size: 12px;
	font-weight: 800;
	letter-spacing: 0.08em;
	box-shadow: 0 8px 18px rgba(8, 127, 112, 0.2);
}

.step-content {
	min-width: 0;
}

.step-content h3 {
	margin: 0 0 4px;
	color: #123f45;
	font-size: 1rem;
	font-weight: 800;
	letter-spacing: -0.02em;
}

.step-content p {
	max-width: 620px;
	margin: 0;
	color: rgba(18, 18, 18, 0.72);
	font-size: 0.88rem;
	line-height: 1.5;
}

@media (max-width: 900px) {
	.how-it-works-title { margin-bottom: 28px; }
	.how-it-works-inner {
		grid-template-columns: 1fr;
		gap: 28px;
	}

	.how-it-works-visual {
		width: min(100%, 720px);
		height: 460px;
		min-height: 0;
		margin: 0 auto;
	}
}

@media (max-width: 600px) {
	.how-it-works-visual { height: 360px; gap: 6px; }
}

</style>

