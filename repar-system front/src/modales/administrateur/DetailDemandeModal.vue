<template>
  <div class="overlay" @click.self="$emit('close')">
    <article role="dialog" aria-modal="true" aria-labelledby="detail-title">
      <header>
        <div>
          <h2 id="detail-title">Détail de la demande</h2>
          <p>Demande #{{ demande.id }}</p>
        </div>
        <button type="button" aria-label="Fermer" @click="$emit('close')"><AppIcon name="close" :size="20"/></button>
      </header>
      <dl>
        <dt>Date de création</dt><dd>{{ dateCreation }}</dd>
        <dt>Client</dt><dd>{{ demande.client }} <span v-if="demande.phone">— {{ demande.phone }}</span></dd>
        <dt>Appareil</dt><dd>{{ demande.device || demande.appareil || 'Non précisé' }}</dd>
        <dt>Catégorie</dt><dd>{{ demande.specialite_detail?.nom || 'Non précisée' }}</dd>
        <dt>Description</dt><dd class="description">{{ demande.description_probleme || 'Aucune description fournie.' }}</dd>
        <dt>Mode d’intervention</dt><dd>{{ modeIntervention }}</dd>
        <dt>Adresse</dt><dd>{{ demande.adresse_intervention || 'Non précisée' }}</dd>
        <dt>Zone</dt><dd>{{ demande.zone }}</dd>
        <dt>Réparateur</dt><dd>{{ demande.reparateur_detail?.nom || 'Aucun réparateur assigné' }}</dd>
        <dt>Statut</dt><dd>{{ demande.status }}</dd>
      </dl>
      <footer><button type="button" @click="$emit('close')">Fermer</button></footer>
    </article>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ demande: { type: Object, required: true } })
defineEmits(['close'])

const dateCreation = computed(() => {
  if (!props.demande.date_creation) return [props.demande.date, props.demande.time].filter(Boolean).join(' à ') || 'Non renseignée'
  const date = new Date(props.demande.date_creation)
  return Number.isNaN(date.getTime()) ? 'Non renseignée' : new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long', timeStyle: 'short' }).format(date)
})
const modeIntervention = computed(() => props.demande.mode_intervention === 'ATELIER' ? 'À l’atelier du réparateur' : 'À domicile')
</script>

<style scoped>
.overlay{position:fixed;inset:0;z-index:30;background:#09285170;display:grid;place-items:center;padding:16px;overflow-y:auto}
article{width:min(560px,100%);max-height:min(90vh,780px);overflow:auto;background:#fff;border-radius:14px;padding:22px;color:#17345f;font-family:Inter,Arial,sans-serif;box-shadow:0 18px 45px #09285135}
header{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:1px solid #e1ecfa;padding-bottom:14px}
header h2{margin:0;color:#12376c;font-size:18px;font-weight:700}header p{margin:5px 0 0;color:#5576a7;font-size:11px}
header button{background:transparent;color:#087f70;font-size:27px;line-height:1}
dl{display:grid;grid-template-columns:minmax(130px, .7fr) 1.3fr;gap:13px 16px;margin:20px 0;font-size:12px;line-height:1.6}
dt{font-weight:700;color:#23466f}dd{margin:0;color:#526e91;overflow-wrap:anywhere}.description{white-space:pre-wrap}
footer{display:flex;justify-content:flex-end;border-top:1px solid #e1ecfa;padding-top:15px}footer button{background:#087f70;color:#fff;border-radius:8px;padding:10px 16px;font-weight:700}
@media(max-width:450px){article{padding:17px}dl{grid-template-columns:1fr;gap:5px}dd{margin-bottom:10px}}
</style>