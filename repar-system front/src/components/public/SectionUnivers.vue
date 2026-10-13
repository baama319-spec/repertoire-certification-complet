<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import imageReparateur from '../../assets/images/image copy 2.png'

const sectionElement = ref(null)
const scrollProgress = ref(0)
const visible = ref(false)
let observer
let frame

const panels = [
  {
    src: imageReparateur,
    alt: 'Technicienne africaine travaillant sur un ordinateur',
    label: 'Technologie',
    text: 'Des outils qui retrouvent leur rythme.',
    role: 'panel-left',
    speed: 10,
  },
  {
    src: 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=1000&q=85',
    alt: 'Électricien en intervention',
    label: 'Électricité',
    text: 'Le bon geste, au bon moment.',
    role: 'panel-right',
    speed: -10,
  },
]

const progress = computed(() => scrollProgress.value)

const updatePosition = () => {
  frame = undefined
  if (!sectionElement.value) return
  const rect = sectionElement.value.getBoundingClientRect()
  const viewport = window.innerHeight || 1
  const raw = (viewport - rect.top) / (viewport + rect.height)
  scrollProgress.value = Math.max(0, Math.min(1, raw))
}

const requestPosition = () => {
  if (frame === undefined) frame = window.requestAnimationFrame(updatePosition)
}

const imageStyle = (image, index) => {
  const movement = (progress.value - 0.18) * image.speed
  return {
    '--image-shift': '0px',
    '--image-y': `${movement}px`,
    '--image-delay': `${index * 80}ms`,
  }
}

onMounted(() => {
  requestPosition()
  window.addEventListener('scroll', requestPosition, { passive: true })
  window.addEventListener('resize', requestPosition, { passive: true })
  observer = new IntersectionObserver(([entry]) => { visible.value = entry.isIntersecting }, { threshold: 0.08 })
  observer.observe(sectionElement.value)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', requestPosition)
  window.removeEventListener('resize', requestPosition)
  if (frame !== undefined) window.cancelAnimationFrame(frame)
  observer?.disconnect()
})
</script>

<template>
  <section ref="sectionElement" class="universe section1" :class="{ 'is-visible': visible }" aria-labelledby="universe-title">
    <header class="universe-intro">
      <h2 id="universe-title">Des mains expertes, <em>des objets qui revivent.</em></h2>
    </header>

    <div class="photo-composition">
      <article class="universe-panel universe-panel-image panel-left" :style="imageStyle(panels[0], 0)">
        <img :src="panels[0].src" :alt="panels[0].alt" loading="lazy" decoding="async">
        <div class="panel-label"><strong>{{ panels[0].label }}</strong><span>{{ panels[0].text }}</span></div>
      </article>
      <article class="universe-panel universe-panel-copy">
        <span class="panel-mark">✦</span>
        <span class="eyebrow">RÉPARER, C'EST PRENDRE SOIN</span>
        <h3>Des mains expertes, <em>pour les objets qui comptent.</em></h3>
        <p>Un réseau de professionnels fiables, proches de vous et prêts à intervenir.</p>
        <RouterLink to="/reparateurs">Trouver un réparateur</RouterLink>
      </article>
      <article class="universe-panel universe-panel-image panel-right" :style="imageStyle(panels[1], 1)">
        <img :src="panels[1].src" :alt="panels[1].alt" loading="lazy" decoding="async">
        <div class="panel-label"><strong>{{ panels[1].label }}</strong><span>{{ panels[1].text }}</span></div>
      </article>
      <!--
      <figure v-for="(image, index) in images" :key="image.src" class="photo-frame" :class="`photo-${image.role}`" :style="imageStyle(image, index)">
        <img :src="image.src" :alt="image.alt" loading="lazy" decoding="async">
        <figcaption>{{ image.label }}</figcaption>
      </figure> -->
    </div>
  </section>
</template>

<style scoped>
.universe {
  --ink: #123f45;
  --muted: #748197;
  min-height: 540px;
  overflow: hidden;
  padding: 28px max(7%, 52px) 42px;
  background: #f5f6fb;
}

.universe-intro {
  max-width: 760px;
  margin: 0 auto 24px;
  text-align: center;
}

.eyebrow {
  color: #087f70;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.2px;
}

.universe h2 {
  max-width: 760px;
  margin: 0;
  color: var(--ink);
  font-size: clamp(30px, 4vw, 48px);
  line-height: 1.12;
  letter-spacing: 0;
}

.universe h2 em {
  color: #087f70;
  font-style: normal;
}

.universe-intro p {
  margin: 0;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.5;
}

.photo-composition {
  position: relative;
  max-width: 1180px;
  height: 420px;
  margin: 0 auto;
}

.photo-frame {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 270px;
  height: 350px;
  margin: 0;
  overflow: hidden;
  border-radius: 10px;
  opacity: 0;
  transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y) + 26px), 0);
  transition: opacity .75s ease var(--image-delay), transform .14s linear;
  will-change: transform, opacity;
}

.is-visible .photo-frame {
  opacity: 1;
  transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y)), 0);
}

.photo-frame::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 55%, #071a2b99);
  pointer-events: none;
}

.photo-frame img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .6s ease;
}

.photo-frame figcaption {
  position: absolute;
  z-index: 1;
  bottom: 14px;
  left: 16px;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .2px;
}

.photo-center-back { z-index: 1; width: 245px; height: 325px; transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y) + 26px), 0); }
.photo-center-middle { z-index: 2; width: 265px; height: 350px; }
.photo-center-down { z-index: 3; width: 285px; height: 375px; }
.is-visible .photo-center-back { transform: translate3d(calc(-50% + var(--image-shift) - 90px), calc(-50% + var(--image-y) - 10px), 0); }
.is-visible .photo-center-middle { transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y) + 8px), 0); }
.is-visible .photo-center-down { transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y) + 25px), 0); }

.photo-composition {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  height: 560px;
  min-height: 0;
  overflow: hidden;
}

.universe-panel {
  position: relative;
  min-width: 0;
  overflow: hidden;
  opacity: 0;
  transform: translate3d(0, 28px, 0);
  transition: opacity .75s ease, transform .75s ease;
  will-change: transform, opacity;
}

.is-visible .universe-panel {
  opacity: 1;
  transform: translate3d(0, var(--image-y, 0px), 0);
}

.universe-panel-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform .65s ease;
}

.universe-panel-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 45%, #071a2b99);
  pointer-events: none;
}

.panel-label {
  position: absolute;
  z-index: 1;
  right: 9%;
  bottom: 9%;
  left: 9%;
  padding: 22px;
  background: #fff;
  color: var(--ink);
  text-align: center;
}

.panel-label strong, .panel-label span { display: block; }
.panel-label strong { color: #087f70; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
.panel-label span { margin-top: 8px; font-family: Georgia, serif; font-size: 21px; line-height: 1.1; }

.universe-panel-copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px 24px;
  background: #0b5960;
  color: #fff;
  text-align: center;
  transition-delay: .12s;
}

.panel-mark {
  display: grid;
  width: 58px;
  height: 58px;
  margin-bottom: 28px;
  place-items: center;
  border: 1px solid #ffffff66;
  border-radius: 50%;
  color: #ffd477;
  font-size: 24px;
}

.universe-panel-copy .eyebrow { color: #b9eee1; }
.universe-panel-copy h3 { margin: 18px 0; font-size: clamp(26px, 3vw, 39px); line-height: 1.08; }
.universe-panel-copy h3 em { color: #ffd477; font-style: normal; }
.universe-panel-copy p { max-width: 260px; margin: 0 0 25px; color: #d2eeee; font-size: 13px; line-height: 1.55; }
.universe-panel-copy a { padding: 12px 17px; background: #ffd477; color: #174b50; font-size: 11px; font-weight: 800; }

@media (hover: hover) and (pointer: fine) {
  .universe-panel-image:hover img { transform: scale(1.035); }
}

@media (hover: hover) and (pointer: fine) {
  .photo-frame:hover img {
    transform: scale(1.035) translate3d(2px, -2px, 0);
  }
}

@media (max-width: 900px) {
  .universe { min-height: 800px; padding: 72px 5% 95px; }
  .universe-intro { margin-bottom: var(--home-title-content-gap, 48px); }
  .photo-composition { height: 510px; }
  .photo-frame { width: 220px; height: 285px; transform: translate3d(calc(-50% + var(--image-shift)), calc(-50% + var(--image-y) + 18px), 0); }
  .is-visible .photo-center-back { transform: translate3d(calc(-50% - 65px), calc(-50% - 8px), 0); }
  .is-visible .photo-center-middle { transform: translate3d(-50%, calc(-50% + 4px), 0); }
  .is-visible .photo-center-down { transform: translate3d(-50%, calc(-50% + 16px), 0); }
}

@media (max-width: 600px) {
  .universe { min-height: auto; padding: 56px 20px 78px; }
  .universe-intro { margin-bottom: var(--home-title-content-gap, 40px); }
  .universe h2 { font-size: 34px; }
  .universe-intro p { max-width: 280px; line-height: 1.5; }
  .photo-composition { display: grid; grid-template-columns: 1fr; height: auto; }
  .universe-panel { min-height: 300px; transform: translate3d(0, 18px, 0); }
  .universe-panel-copy { min-height: 350px; padding: 35px 25px; order: 2; }
  .panel-left { order: 1; }
  .panel-right { order: 3; }
  .panel-label { right: 7%; bottom: 7%; left: 7%; padding: 16px; }
  .panel-label span { font-size: 18px; }
  .photo-frame figcaption { bottom: 10px; left: 11px; font-size: 10px; }
}

@media (prefers-reduced-motion: reduce) {
  .photo-frame, .is-visible .photo-frame { transform: none; transition: opacity .25s ease; }
  .photo-frame img { transition: none; }
}
</style>
