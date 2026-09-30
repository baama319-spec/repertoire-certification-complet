<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const howSection = ref(null)
const isVisible = ref(false)
let observer

onMounted(() => {
  observer = new IntersectionObserver(([entry]) => {
    isVisible.value = entry.isIntersecting
  }, { threshold: 0.18 })
  observer.observe(howSection.value)
})

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <section ref="howSection" id="how" class="how-section" :class="{ 'is-visible': isVisible }" aria-labelledby="how-title">
    <header class="how-heading">
      <span class="eyebrow">COMMENT ÇA MARCHE</span>
      <h2 id="how-title">Une réparation simple</h2>
    </header>

    <div class="how-steps">
      <article class="how-step">
        <div class="step-heading"><div class="step-number">01</div><h3>Décrivez votre besoin</h3></div>
        <div class="demo-card search-demo"><div class="demo-top"><span>☰</span></div><strong>Que faut-il réparer ?</strong><div class="demo-field">▯　Écran de téléphone <span>⌄</span></div><div class="demo-field">●　Dakar Plateau <span>⌾</span></div><div class="demo-button">⌕　 Rechercher</div></div>
      </article>
      <div class="step-line" aria-hidden="true">→</div>
      <article class="how-step">
        <div class="step-heading"><div class="step-number">02</div><h3>Trouvez un réparateur proche</h3></div>
        <div class="demo-card map-demo"><div class="map-surface"><span class="map-pin pin-one">●</span><span class="map-pin pin-two">●</span><b>Dakar</b><small>Votre position</small></div><div class="map-profile"><span class="mini-avatar">⚒</span><span><b>Mamadou Fall</b><small>★ 4.9 · 1.2 km</small></span><em>Disponible</em></div></div>
      </article>
      <div class="step-line" aria-hidden="true">→</div>
      <article class="how-step">
        <div class="step-heading"><div class="step-number">03</div><h3>Échangez et planifiez</h3></div>
        <div class="demo-card appointment-demo"><div class="demo-top"><span>⋯</span></div><div class="accepted">●　 Demande acceptée</div><div class="appointment-row">▣　Aujourd'hui · 15:30 <span>›</span></div><div class="message-row"><span class="mini-avatar">•••</span><b>Mamadou Fall</b><small>Je confirme votre demande.</small></div><div class="demo-button">→　 Suivre l’intervention</div></div>
      </article>
    </div>

    <RouterLink class="how-action" to="/reparateurs">Commencer une recherche <span>→</span></RouterLink>
  </section>
</template>

<style scoped>
.how-section {
  padding: 82px max(7%, 52px) 140px;
  background: #fff;
  color: #123f45;
  text-align: center;
}

.how-heading { max-width: 720px; margin: 0 auto var(--home-title-content-gap, 64px); opacity: 0; transform: translate3d(0, 22px, 0); transition: opacity .65s ease, transform .65s ease; }
.is-visible .how-heading { opacity: 1; transform: translate3d(0, 0, 0); }
.eyebrow { color: #087f70; font-size: 10px; font-weight: 800; letter-spacing: 1.2px; }
.how-heading h2 { margin: 14px 0 16px; font-size: clamp(30px, 4vw, 48px); line-height: 1.12; }
.how-heading h2 em { color: #087f70; font-style: normal; }
.how-heading p { max-width: 510px; margin: auto; color: #748197; font-size: 14px; line-height: 1.55; }
.how-steps { display: grid; grid-template-columns: 1fr 48px 1fr 48px 1fr; align-items: start; max-width: 1120px; margin: auto; }
.how-step { position: relative; min-width: 0; opacity: 0; transform: translate3d(0, 30px, 0); transition: opacity .65s ease, transform .65s ease; }
.is-visible .how-step { opacity: 1; transform: translate3d(0, 0, 0); }
.is-visible .how-step:nth-of-type(1) { transition-delay: .12s; }
.is-visible .how-step:nth-of-type(2) { transition-delay: .25s; }
.is-visible .how-step:nth-of-type(3) { transition-delay: .38s; }
.step-heading { display: flex; align-items: center; gap: 15px; text-align: left; }
.step-number { display: grid; flex: none; width: 46px; height: 46px; place-items: center; border-radius: 50%; background: #087f70; color: #fff; font-size: 16px; font-weight: 800; }
.how-step h3 { margin: 0; color: #123f45; font-size: 16px; line-height: 1.25; }
.how-step > p { min-height: 40px; margin: 14px 0 14px 61px; color: #748197; font-size: 11px; line-height: 1.5; text-align: left; }
.demo-card { margin-top: 18px; }
.step-line { align-self: center; margin-top: 70px; color: #087f70; font-size: 30px; font-weight: 300; opacity: 0; transform: translate3d(-10px, 0, 0); transition: opacity .5s ease, transform .5s ease; }
.is-visible .step-line { opacity: 1; transform: translate3d(0, 0, 0); }
.demo-card { min-height: 185px; padding: 14px; border: 1px solid #d7ebe7; border-radius: 9px; background: #fff; box-shadow: 0 8px 22px #174b5010; color: #174b50; text-align: left; }
.demo-top { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid #edf3f1; font-size: 10px; }
.demo-top b:first-letter { color: #087f70; }
.search-demo > strong { display: block; margin: 13px 0 9px; font-size: 12px; }
.demo-field, .appointment-row { display: flex; align-items: center; justify-content: space-between; margin-top: 7px; padding: 9px; border: 1px solid #e0eeeb; border-radius: 6px; color: #69838a; font-size: 9px; }
.demo-field span, .appointment-row span { color: #087f70; font-weight: 800; }
.demo-button { margin-top: 9px; padding: 9px; border-radius: 5px; background: #087f70; color: #fff; font-size: 9px; font-weight: 800; text-align: center; }
.map-surface { position: relative; height: 104px; overflow: hidden; border-radius: 6px; background: linear-gradient(135deg, #c9eaf1, #edf7ee 48%, #d7eee9); }
.map-surface::before, .map-surface::after { content: ''; position: absolute; background: #fff8; transform: rotate(-25deg); }
.map-surface::before { top: 52px; right: -15px; left: -15px; height: 7px; }
.map-surface::after { top: 25px; right: 30px; width: 7px; height: 120px; }
.map-surface b { position: absolute; bottom: 11px; left: 14px; color: #174b50; font-size: 13px; }
.map-surface small { position: absolute; top: 9px; left: 50%; padding: 4px 7px; border-radius: 8px; background: #087f70; color: #fff; font-size: 7px; transform: translateX(-50%); white-space: nowrap; }
.map-pin { position: absolute; z-index: 1; display: grid; width: 17px; height: 17px; place-items: center; border: 2px solid #fff; border-radius: 50% 50% 50% 0; background: #087f70; color: #fff; font-size: 7px; transform: rotate(-45deg); }
.map-pin::first-letter { transform: rotate(45deg); }
.pin-one { top: 29px; left: 35%; }.pin-two { top: 48px; right: 25%; }
.map-profile { display: flex; align-items: center; gap: 8px; padding-top: 10px; font-size: 9px; }.map-profile span:nth-child(2) { display: grid; gap: 3px; }.map-profile small { color: #e39d16; }.map-profile em { margin-left: auto; color: #159b78; font-size: 8px; font-style: normal; }
.mini-avatar { display: grid; width: 28px; height: 28px; place-items: center; border-radius: 50%; background: #e5f4f0; color: #087f70; font-size: 10px; }
.accepted { margin-top: 13px; padding: 8px; border-radius: 6px; background: #e4f7f1; color: #159b78; font-size: 9px; font-weight: 800; }.message-row { display: grid; grid-template-columns: 28px 1fr; gap: 2px 8px; align-items: center; margin-top: 9px; padding: 8px; border-radius: 6px; background: #f4f8f7; font-size: 9px; }.message-row .mini-avatar { grid-row: span 2; }.message-row small { color: #748197; font-size: 8px; }
.how-action { display: inline-flex; align-items: center; gap: 15px; margin-top: 65px; padding: 13px 19px; border-radius: 7px; background: #087f70; color: #fff; font-size: 11px; font-weight: 800; opacity: 0; transform: translate3d(0, 18px, 0); transition: opacity .6s ease .55s, transform .6s ease .55s, background .2s ease; }
.is-visible .how-action { opacity: 1; transform: translate3d(0, 0, 0); }
.how-action:hover { background: #076b64; }
.how-action span { font-size: 18px; line-height: 10px; }
@media (max-width: 800px) {
  .how-section { padding: 64px 24px 100px; }
  .how-heading { margin-bottom: var(--home-title-content-gap, 48px); }
  .how-steps { display: block; max-width: 420px; }
  .how-step { margin-bottom: 28px; }
  .step-heading { gap: 12px; }
  .step-number { width: 40px; height: 40px; font-size: 14px; }
  .how-step > p { min-height: 0; margin: 10px 0 14px 52px; }
  .step-line { margin: -14px 0 14px; text-align: center; transform: rotate(90deg); }
  .how-action { margin-top: 45px; }
}
@media (prefers-reduced-motion: reduce) {
  .how-heading, .how-step, .step-line, .how-action, .is-visible .how-heading, .is-visible .how-step, .is-visible .step-line, .is-visible .how-action { opacity: 1; transform: none; transition: none; }
}
</style>
