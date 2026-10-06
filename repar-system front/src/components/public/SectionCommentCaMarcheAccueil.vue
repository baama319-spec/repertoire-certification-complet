<script setup>
import { ref } from 'vue'

const etapes = [
  {
    numero: '01',
    icon: 'clipboard',
    titre: 'Décrivez votre besoin',
    description: 'Choisissez votre appareil et expliquez simplement ce qui ne fonctionne pas.',
    detail: '2 minutes suffisent',
  },
  {
    numero: '02',
    icon: 'search',
    titre: 'Trouvez le bon expert',
    description: 'Comparez les profils vérifiés, leurs spécialités et les avis près de chez vous.',
    detail: 'Des pros vérifiés',
  },
  {
    numero: '03',
    icon: 'message',
    titre: 'Suivez la réparation',
    description: 'Échangez avec votre réparateur et suivez votre demande jusqu’à sa résolution.',
    detail: 'Vous gardez le contrôle',
  },
]

const etapeActive = ref(0)
</script>

<template>
  <section class="how-it-works" aria-labelledby="how-title">
    <div class="how-inner">
      <header class="how-heading">
        <span class="how-kicker"><AppIcon name="sparkles" :size="14"/> SIMPLE, DU DÉBUT À LA FIN</span>
        <h2 id="how-title">Comment ça <em>marche&nbsp;?</em></h2>
        <p>En quelques étapes, trouvez une solution fiable pour réparer ce qui compte.</p>
      </header>

      <div class="how-progress" aria-hidden="true">
        <span v-for="(etape, index) in etapes" :key="etape.numero" :class="{ active: index <= etapeActive }"></span>
      </div>
      <div class="how-cards">
        <button
          v-for="(etape, index) in etapes"
          :key="etape.numero"
          class="how-card"
          :class="{ active: index === etapeActive }"
          type="button"
          :aria-pressed="index === etapeActive"
          @mouseenter="etapeActive = index"
          @focus="etapeActive = index"
          @click="etapeActive = index"
        >
          <span class="card-top"><span class="step-number">{{ etape.numero }}</span><span class="step-icon"><AppIcon :name="etape.icon" :size="23"/></span></span>
          <span class="card-copy"><strong>{{ etape.titre }}</strong><span>{{ etape.description }}</span></span>
          <span class="step-detail"><AppIcon name="check-circle" :size="15"/> {{ etape.detail }}</span>
        </button>
      </div>

      <div class="how-bottom">
        <span><AppIcon name="shield-check" :size="18"/> Des réparateurs vérifiés, à proximité</span>
        <RouterLink to="/diagnostic">Commencer maintenant <AppIcon name="arrow-right" :size="16"/></RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.how-it-works{position:relative;overflow:hidden;padding:86px 28px 76px;background:linear-gradient(145deg,#f4fbfa 0%,#fff 48%,#f2f8ff 100%);color:#102a46}
.how-it-works::before,.how-it-works::after{position:absolute;width:300px;height:300px;border-radius:50%;background:#c4f1e655;filter:blur(4px);content:'';pointer-events:none}
.how-it-works::before{top:-205px;left:-90px}.how-it-works::after{right:-160px;bottom:-230px;background:#cae2ff55}
.how-inner{position:relative;z-index:1;max-width:1120px;margin:0 auto}
.how-heading{max-width:680px;margin:0 auto 46px;text-align:center}
.how-kicker{display:inline-flex;align-items:center;gap:7px;padding:8px 13px;border:1px solid #d5eeea;border-radius:30px;background:#fff;color:#087f70;font-size:10px;font-weight:800;letter-spacing:1.1px}
.how-heading h2{margin:17px 0 10px;color:#102a46;font-size:clamp(32px,4vw,46px);font-weight:800;letter-spacing:-1.6px;line-height:1.1}
.how-heading h2 em{color:#087f70;font-style:normal}
.how-heading p{margin:0;color:#71839a;font-size:14px;line-height:1.6}
.how-progress{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;max-width:850px;margin:0 auto 13px}
.how-progress span{height:3px;border-radius:4px;background:#dfe9ed;transition:background .25s ease}
.how-progress span.active{background:linear-gradient(90deg,#0ca889,#49c8ad)}
.how-cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.how-card{display:flex;min-height:248px;flex-direction:column;align-items:stretch;padding:22px 21px 18px;border:1px solid #e1eaf0;border-radius:16px;background:#ffffffd9;color:inherit;text-align:left;box-shadow:0 8px 24px #12365408;cursor:pointer;transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease,background .22s ease}
.how-card:hover,.how-card:focus-visible,.how-card.active{transform:translateY(-4px);border-color:#a8ded5;background:#fff;box-shadow:0 15px 35px #087f7015;outline:none}
.card-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:27px}
.step-number{color:#8ba0b0;font-size:12px;font-weight:800;letter-spacing:1px}
.step-icon{display:grid;width:48px;height:48px;place-items:center;border:1px solid #d4efea;border-radius:14px;background:linear-gradient(145deg,#effbf8,#def5ef);color:#078875;transition:transform .2s ease}
.how-card.active .step-icon{transform:rotate(-5deg) scale(1.05)}
.card-copy{display:grid;gap:9px}
.card-copy strong{color:#173652;font-size:17px;letter-spacing:-.3px}
.card-copy>span{min-height:61px;color:#71839a;font-size:12px;line-height:1.6}
.step-detail{display:flex;align-items:center;gap:7px;margin-top:auto;padding-top:15px;border-top:1px solid #eef2f4;color:#168675;font-size:11px;font-weight:700}
.how-bottom{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:28px;padding:17px 19px;border:1px solid #e0ecec;border-radius:12px;background:#ffffffb8}
.how-bottom>span,.how-bottom>a{display:inline-flex;align-items:center;gap:9px}
.how-bottom>span{color:#58738a;font-size:12px;font-weight:600}
.how-bottom>span :deep(svg){color:#098977}
.how-bottom>a{padding:11px 15px;border-radius:8px;background:#087f70;color:#fff;font-size:12px;font-weight:800;text-decoration:none;transition:background .18s ease,transform .18s ease}
.how-bottom>a:hover{transform:translateY(-1px);background:#066d61}
@media(max-width:760px){.how-it-works{padding:65px 20px}.how-heading{margin-bottom:33px}.how-cards{grid-template-columns:1fr;gap:11px}.how-progress{display:none}.how-card{min-height:0;padding:17px}.card-top{margin-bottom:14px}.card-copy>span{min-height:0}.step-detail{margin-top:14px;padding-top:11px}.how-bottom{align-items:stretch;flex-direction:column}.how-bottom>a{justify-content:center}}
@media(prefers-reduced-motion:reduce){.how-card,.step-icon,.how-bottom>a{transition:none}}
</style>
