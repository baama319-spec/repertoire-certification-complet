<script setup>
defineProps({ avis: { type: Object, required: true } })
</script>
<template>
  <article class="carte-avis">
    <section class="client"><span class="avatar">{{ avis.initiales }}</span><div><h2>{{ avis.client }}</h2><p class="etoiles">★★★★★ <small>{{ avis.note }} / 5.0</small></p></div><p class="prestation">⚒　 Prestation :　{{ avis.prestation }}</p></section>
    <section class="retour"><p>{{ avis.texte }}</p><div><span>●　 Intervention validée</span><small>♦　 {{ avis.lieu }}</small></div></section>
    <aside><p>▣　 {{ avis.date }}</p><button>⋮</button></aside>
  </article>
</template>
<style scoped>
.carte-avis{min-height:165px;display:grid;grid-template-columns:35% 45% 20%;position:relative;border:1px solid #dceeea;border-radius:8px;padding:18px;color:#0b377d}.client{position:relative;padding-left:68px}.avatar{position:absolute;left:0;top:0;display:grid;place-items:center;width:52px;height:52px;border-radius:50%;background:linear-gradient(135deg,#2384ff,#075fd9);color:white;font-size:13px;font-weight:800}.client h2{margin:5px 0 11px;font-size:15px}.etoiles{margin:0;color:#ffb51c;font-size:21px;letter-spacing:1px}.etoiles small{color:#5879ac;font-size:13px;letter-spacing:0;font-weight:600}.prestation{position:absolute;top:70px;left:0;color:#6684b6;font-size:12px;white-space:nowrap}.retour>p{min-height:82px;margin:0;padding:13px 20px;border-radius:9px;background:linear-gradient(105deg,#f3f7fd,#f7faff);font-size:14px;line-height:1.75}.retour>div{display:flex;align-items:center;gap:25px;margin-top:11px;font-size:12px}.retour span{border-radius:18px;background:#dff8ef;color:#0aab77;padding:6px 13px}.retour small{color:#6684b6;font-size:12px}aside{display:flex;align-items:flex-start;justify-content:flex-end;gap:18px;color:#6684b6;font-size:12px}aside p{margin:8px 0}aside button{border:0;background:transparent;color:#41689f;font-size:22px}@media(max-width:1050px){.carte-avis{grid-template-columns:1fr;gap:14px}.client{min-height:100px}.retour>p{min-height:auto}.retour{padding-right:0}aside{position:absolute;right:12px;top:8px}}@media(max-width:600px){.prestation{white-space:normal;padding-right:20px}.retour>div{gap:8px;flex-wrap:wrap}.etoiles{font-size:16px}}
</style>
