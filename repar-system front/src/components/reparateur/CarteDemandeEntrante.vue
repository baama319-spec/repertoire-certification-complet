<script setup>
import Avatar from '../commun/Avatar.vue'

defineProps({ demande: { type: Object, required: true }, selectionnee: Boolean })
defineEmits(['selectionner'])
</script>

<template>
  <button class="carte-demande" :class="{ selectionnee }" @click="$emit('selectionner', demande)">
    <span class="avatar-demande">
      <Avatar :photo="demande.photo" :nom="demande.client || 'Client'" :alt="`Photo de ${demande.client || 'client'}`" />
    </span>
    <span class="demande-contenu">
      <span class="demande-titre"><b>{{ demande.client }}</b><em v-if="demande.statut !== 'Nouveau'" :class="demande.couleur">{{ demande.statut }}</em><small>{{ demande.temps }}</small></span>
      <span class="demande-probleme"><AppIcon name="smartphone" :size="15" /> {{ demande.appareil }}<template v-if="demande.panne"> · {{ demande.panne }}</template></span>
      <span class="demande-lieu"><AppIcon name="pin" :size="15" /> {{ demande.zone }}<template v-if="demande.distance"> ({{ demande.distance }})</template></span>
    </span>
    <AppIcon class="chevron" name="chevron-right" :size="20" />
  </button>
</template>

<style scoped>
.carte-demande{position:relative;display:flex;box-sizing:border-box;width:100%;min-height:142px;align-items:center;gap:14px;margin:0 0 12px;padding:15px 14px;border:1px solid #dfeee8;border-radius:12px;background:#fff;color:#123366;text-align:left;font-family:inherit;font-weight:400;transition:border-color .18s ease,box-shadow .18s ease,transform .18s ease}
.carte-demande:not(.selectionnee){background:#fff;border-color:#dfeee8}
.carte-demande.selectionnee{border-color:#067563;background:linear-gradient(112deg,#eafaf5 10%,#dff6f0);box-shadow:0 2px 8px rgba(6,117,99,.12)}
.avatar-demande{width:54px;height:54px}
.demande-contenu{display:grid;min-width:0;max-width:none;flex:1;gap:12px}
.demande-titre{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:4px 10px;font-size:14px;line-height:1.2}
.demande-titre b{max-width:none;color:#12366b;font-size:15px;font-weight:750;line-height:normal;overflow-wrap:anywhere;word-break:normal}
.demande-titre small{justify-self:end;width:auto;color:#7388a7;font-size:11px;line-height:1.35;text-align:right;white-space:nowrap}
.demande-probleme,.demande-lieu{display:flex;align-items:flex-start;gap:6px;font-size:12px;line-height:1.4;overflow-wrap:anywhere}
.demande-probleme :deep(svg),.demande-lieu :deep(svg){width:auto;height:auto;flex:none;margin-top:1px}
.chevron{position:static;align-self:center;flex:none;margin-left:auto;transform:none;color:#7891b7}
@media(max-width:900px){.carte-demande{min-height:132px;align-items:center;gap:11px;margin-bottom:9px;padding:12px}.avatar-demande{width:48px;height:48px}.demande-contenu{gap:10px;max-width:none}.demande-titre{font-size:13px}.demande-titre b{font-size:14px}.demande-titre small{width:auto;font-size:10px;white-space:normal}.demande-probleme,.demande-lieu{font-size:12px}}
</style>
