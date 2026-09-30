<script setup>
defineProps({ demande: { type: Object, required: true }, selectionnee: Boolean })
defineEmits(['selectionner'])
</script>

<template>
  <button class="carte-demande" :class="{ selectionnee }" @click="$emit('selectionner', demande)">
    <span class="avatar-demande" :class="demande.couleur">{{ demande.initiales }}</span>
    <span class="demande-contenu">
      <span class="demande-titre"><b>{{ demande.client }}</b><em v-if="demande.statut !== 'Nouveau'" :class="demande.couleur">{{ demande.statut }}</em><small>{{ demande.temps }}</small></span>
      <span class="demande-probleme">▣　{{ demande.appareil }}　•　{{ demande.panne }}</span>
      <span class="demande-lieu">●　{{ demande.zone }}<template v-if="demande.distance"> ({{ demande.distance }})</template></span>
    </span>
    <span class="chevron">›</span>
  </button>
</template>

<style scoped>
.carte-demande{width:100%;min-height:135px;display:flex;align-items:flex-start;gap:18px;padding:17px 17px;margin:0 0 18px;border:1px solid #dfe9f8;border-radius:8px;background:#fff;color:#123366;text-align:left;font-family:inherit;font-weight:400}.carte-demande.selectionnee{border-color:#1c73ff;background:linear-gradient(112deg,#fff 10%,#edf5ff);box-shadow:0 2px 6px #1d70f51e}.avatar-demande{display:grid;place-items:center;width:47px;height:47px;flex:none;border-radius:50%;color:white;font-size:11px;font-weight:800}.jaune{background:#ffc741}.bleu{background:#1474ec}.rouge{background:#ff4052}.demande-contenu{display:grid;gap:13px;min-width:0;flex:1}.demande-titre{display:flex;align-items:center;gap:17px;font-size:14px}.demande-titre b{color:#11346c}.demande-titre small{font-size:12px;color:#7d91b3;font-weight:400}.demande-titre em{padding:5px 13px;border-radius:15px;font-size:10px;font-style:normal;font-weight:700}.demande-titre em.bleu{background:#e0efff;color:#1474ec}.demande-titre em.rouge{background:#ffe5e8;color:#ff3b4c}.demande-probleme,.demande-lieu{font-size:12px;color:#193f7c}.demande-lieu{color:#7890b4}.chevron{align-self:center;color:#7f94b6;font-size:29px;font-weight:400}@media(max-width:900px){.carte-demande{min-height:105px;margin-bottom:10px;padding:12px}.avatar-demande{width:36px;height:36px}.demande-contenu{gap:8px}.demande-titre{font-size:11px}}
</style>
