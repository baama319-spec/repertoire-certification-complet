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
  <section ref="howSection" id="how" class="how-section" :class="{ 'is-visible': isVisible }" aria-label="Les avantages de ReparSystem">
    <div class="feature-cards">
      <article class="feature-card">
        <span class="feature-label">SIMPLE & RAPIDE</span>
        <div class="feature-art art-simple" aria-hidden="true"><span>01</span></div>
        <div class="feature-copy"><h2>Votre panne,<br>en quelques mots.</h2><p>Décrivez votre appareil et le problème rencontré. Nous vous aidons à préciser votre besoin, sans démarches compliquées.</p></div>
      </article>

      <article class="feature-card">
        <span class="feature-label">DES EXPERTS PRÈS DE VOUS</span>
        <div class="feature-art art-proximity" aria-hidden="true"><span>02</span></div>
        <div class="feature-copy"><h2>Le bon réparateur,<br>au bon endroit.</h2><p>Comparez des profils de professionnels et trouvez un réparateur qualifié dans votre zone d’intervention.</p></div>
      </article>

      <article class="feature-card feature-card-dark">
        <span class="feature-label">UN SUIVI EN TOUTE CONFIANCE</span>
        <div class="feature-art art-follow" aria-hidden="true"><span>03</span></div>
        <div class="feature-copy"><h2>Votre réparation,<br>bien accompagnée.</h2><p>Échangez directement avec le professionnel, organisez l’intervention et retrouvez vos demandes depuis votre espace.</p></div>
      </article>
    </div>
    <RouterLink class="how-action" to="/reparateurs">Trouver un réparateur <span aria-hidden="true">↗</span></RouterLink>
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

.how-section {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding: 34px max(7%, 52px) 66px;
  background: radial-gradient(ellipse at 50% 45%, #fff 0%, #f7fcfd 56%, #edf9fa 100%);
  color: #142d43;
}
.how-section::before, .how-section::after {
  position: absolute;
  z-index: -1;
  width: 340px;
  height: 250px;
  border: 1px solid #9be7ed88;
  border-radius: 50%;
  background: radial-gradient(ellipse, #6ed7df55, #a8eff000 70%);
  content: '';
  filter: blur(2px);
}
.how-section::before { top: -170px; left: -130px; }
.how-section::after { right: -155px; bottom: -190px; }
.how-heading { margin-bottom: 38px; }
.eyebrow { display: inline-block; padding: 9px 17px; border-radius: 30px; background: #f2fbfbcc; color: #168b88; font-size: 10px; letter-spacing: 4px; }
.how-heading h2 { margin: 18px 0 14px; color: #12283e; font-size: clamp(34px, 4vw, 52px); font-weight: 800; letter-spacing: -1.5px; }
.how-heading h2 em { background: linear-gradient(90deg, #47c7bd, #08796e); background-clip: text; color: transparent; }
.how-heading p { color: #8094aa; font-size: 16px; line-height: 1.55; }
.how-steps { grid-template-columns: minmax(0, 1fr) 48px minmax(0, 1fr) 48px minmax(0, 1fr); max-width: 1270px; align-items: center; }
.step-card { min-height: 300px; box-sizing: border-box; padding: 56px 46px 22px; border: 1px solid #d9f0f2; border-radius: 25px; background: linear-gradient(135deg, #ffffffd9, #effbfcaa); box-shadow: 0 20px 44px #5b9eaa12, inset 0 1px 0 #fff; text-align: left; backdrop-filter: blur(12px); }
.step-number { position: absolute; top: 12px; left: 20px; width: 48px; height: 48px; background: linear-gradient(145deg, #18c6a0, #078471); box-shadow: 0 7px 18px #0a9e8730; font-size: 16px; }
.step-icon { display: grid; width: 78px; height: 78px; margin-bottom: 12px; place-items: center; border: 1px solid #d7f2f0; border-radius: 20px; background: linear-gradient(145deg, #f7ffff, #dcf6f4); box-shadow: 0 8px 20px #4bbeb41a, inset 0 1px 0 #fff; }
.step-icon svg { width: 34px; height: 34px; fill: none; stroke: #078f80; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.6; }
.step-card h3 { margin: 0 0 7px; color: #142d43; font-size: 20px; letter-spacing: -.4px; }
.step-card > p { min-height: 44px; margin: 0 0 12px; color: #6e859c; font-size: 14px; line-height: 1.55; }
.step-benefit { display: flex; align-items: center; gap: 10px; min-height: 36px; padding: 0 13px; border-radius: 10px; background: #f4fbfbcc; color: #16877f; font-size: 11px; font-weight: 700; }
.step-benefit span { display: grid; width: 22px; height: 22px; place-items: center; border: 2px solid #179b8d; border-radius: 50%; font-size: 14px; }
.map-card { background: linear-gradient(135deg, #ffffffd9, #e8f9f9bb); }
.map-decoration { position: absolute; top: 0; right: 0; width: 54%; height: 58%; overflow: hidden; opacity: .7; pointer-events: none; }
.map-decoration::before, .map-decoration::after { position: absolute; top: 43%; left: -10%; width: 125%; height: 13px; border-radius: 50%; background: #fff; content: ''; transform: rotate(-22deg); }
.map-decoration::after { top: 22%; left: 24%; width: 15px; height: 140%; transform: rotate(35deg); }
.map-decoration span, .map-decoration i, .map-decoration b { position: absolute; z-index: 1; color: #12ad9a; font-size: 34px; font-style: normal; }
.map-decoration span { top: 28px; right: 31%; }.map-decoration i { top: 68px; right: 13%; font-size: 22px; }.map-decoration b { top: 45px; left: 20%; color: #a2dedd; font-size: 26px; }
.appointment-decoration { position: absolute; top: 17px; right: 15px; display: flex; width: 112px; height: 48px; align-items: center; justify-content: space-around; border: 1px solid #c8f5ef; border-radius: 14px; background: #d9faf2bd; box-shadow: 0 8px 18px #54cdb61c; color: #0d9d83; transform: rotate(14deg); }
.appointment-decoration span { display: grid; width: 29px; height: 29px; place-items: center; border-radius: 50%; background: #079780; color: white; }.appointment-decoration i { font-style: normal; letter-spacing: 2px; }
.step-line { margin-top: 0; color: #15867d; font-size: 27px; }
.how-action { margin-top: 48px; padding: 17px 35px; border-radius: 32px; background: linear-gradient(100deg, #087e72, #10b88c); box-shadow: 0 12px 24px #079b8130; font-size: 14px; }
.how-action:hover { background: linear-gradient(100deg, #076b64, #0a9d7c); }
@media (max-width: 1000px) {
  .how-section { padding-right: 32px; padding-left: 32px; }
  .how-steps { grid-template-columns: minmax(0, 1fr) 30px minmax(0, 1fr) 30px minmax(0, 1fr); }
  .step-card { padding-right: 22px; padding-left: 22px; }
  .step-card h3 { font-size: 17px; }
  .step-card > p { font-size: 12px; }
}
@media (max-width: 800px) {
  .how-section { padding: 54px 22px 72px; }
  .how-heading { margin-bottom: 34px; }
  .how-heading h2 { font-size: 38px; }
  .how-heading p { font-size: 14px; }
  .how-steps { display: block; max-width: 520px; }
  .step-card { min-height: 270px; margin-bottom: 20px; padding: 48px 28px 20px; }
  .step-card h3 { font-size: 19px; }
  .step-card > p { font-size: 13px; }
  .step-line { display: none; }
  .desktop-break { display: none; }
  .map-decoration { width: 48%; }
}

.how-section {
  padding: 8px max(1.7vw, 16px) 42px;
  background: #d8dddf;
  color: #080a0b;
}
.how-section::before, .how-section::after { display: none; }
.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  max-width: 1800px;
  margin: 0 auto;
}
.feature-card {
  position: relative;
  display: flex;
  min-width: 0;
  min-height: clamp(540px, 76vh, 760px);
  flex-direction: column;
  overflow: hidden;
  padding: 28px 30px 30px;
  border: 1px solid #131719;
  border-radius: 34px;
  background: #fff;
  color: #080a0b;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity .65s ease, transform .65s ease, background .25s ease;
}
.is-visible .feature-card { opacity: 1; transform: translateY(0); }
.is-visible .feature-card:nth-child(2) { transition-delay: .12s; }
.is-visible .feature-card:nth-child(3) { transition-delay: .24s; }
.feature-card-dark { border-color: #050606; background: #050606; color: #fff; }
.feature-label { position: relative; z-index: 1; font-size: clamp(12px, 1.15vw, 17px); font-weight: 500; letter-spacing: -.2px; }
.feature-art {
  position: relative;
  display: grid;
  width: min(100%, 390px);
  flex: 1;
  min-height: 270px;
  align-self: center;
  place-items: center;
  color: #080a0b;
}
.feature-art::before {
  width: 100%;
  height: 100%;
  background-image: radial-gradient(circle, currentColor 2.7px, transparent 3.25px);
  background-position: center;
  background-size: 14px 14px;
  content: '';
  -webkit-mask-image: radial-gradient(ellipse 42% 34% at 50% 50%, #000 35%, transparent 72%);
  mask-image: radial-gradient(ellipse 42% 34% at 50% 50%, #000 35%, transparent 72%);
}
.feature-art span { position: absolute; right: 0; bottom: 0; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.art-simple::before {
  -webkit-mask-image: radial-gradient(ellipse 46% 39% at 48% 50%, #000 37%, transparent 72%);
  mask-image: radial-gradient(ellipse 46% 39% at 48% 50%, #000 37%, transparent 72%);
  transform: rotate(-25deg) scale(.92);
}
.art-proximity::before {
  -webkit-mask-image: radial-gradient(ellipse 27% 48% at 50% 50%, #000 34%, transparent 72%);
  mask-image: radial-gradient(ellipse 27% 48% at 50% 50%, #000 34%, transparent 72%);
  transform: rotate(15deg) scale(.95);
}
.art-follow { color: #fff; }
.art-follow::before {
  background-size: 14px 14px;
  -webkit-mask-image: radial-gradient(ellipse 40% 37% at 50% 50%, #000 48%, transparent 70%);
  mask-image: radial-gradient(ellipse 40% 37% at 50% 50%, #000 48%, transparent 70%);
}
.feature-copy { margin-top: auto; text-align: left; }
.feature-copy h2 { margin: 0 0 14px; color: inherit; font-size: clamp(24px, 2.3vw, 36px); font-weight: 600; letter-spacing: -1.1px; line-height: 1.07; }
.feature-copy p { max-width: 420px; margin: 0; color: #30373b; font-size: clamp(13px, 1.1vw, 17px); line-height: 1.48; }
.feature-card-dark .feature-copy p { color: #e2e4e5; }
.how-action { margin-top: 26px; padding: 15px 22px; border-radius: 28px; background: #087f70; font-size: 13px; }
.how-action:hover { background: #06665d; }
@media (max-width: 800px) {
  .how-section { padding: 8px 0 34px; }
  .feature-cards { display: flex; gap: 10px; overflow-x: auto; padding: 0 16px 12px; scroll-snap-type: x mandatory; scrollbar-width: none; }
  .feature-cards::-webkit-scrollbar { display: none; }
  .feature-card { min-width: min(82vw, 420px); min-height: 600px; padding: 24px 23px 25px; border-radius: 28px; scroll-snap-align: center; }
  .feature-label { font-size: 13px; }
  .feature-art { min-height: 300px; }
  .feature-copy h2 { font-size: 30px; }
  .feature-copy p { font-size: 14px; }
}
@media (prefers-reduced-motion: reduce) {
  .feature-card, .is-visible .feature-card { opacity: 1; transform: none; transition: none; }
}
</style>
