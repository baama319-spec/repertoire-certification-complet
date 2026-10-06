<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../services/api'
import { ajouterRealisation, modifierRealisation } from '../../services/serviceRealisations'
import { minLengthMessage, requiredMessage } from '../../utils/formValidation'
const emit = defineEmits(['fermer', 'publie'])
const props = defineProps({ realisation: { type: Object, default: null } })
const titre=ref(props.realisation?.titre || ''), description=ref(props.realisation?.description || ''), specialite=ref(props.realisation?.specialite || ''), specialites=ref([]), avant=ref(null), apres=ref(null), erreur=ref(''), envoi=ref(false)
onMounted(async()=>{try{const data=await api('/specialites/');specialites.value=data.results||data}catch(e){erreur.value=e.message}})
const fichier=(event,type)=>{const selection=event.target.files?.[0]||null;if(type==='avant')avant.value=selection;else apres.value=selection}
const validerFormulaire = () => {
  const messages = [
    requiredMessage(titre.value, 'Le titre de la réparation'),
    requiredMessage(specialite.value, 'La spécialité'),
    minLengthMessage(description.value, 'La description du travail', 10),
  ].filter(Boolean)

  if (messages.length) {
    throw new Error(messages[0])
  }

  if (avant.value && !['image/jpeg', 'image/png', 'image/webp'].includes(avant.value.type)) {
    throw new Error('La photo avant doit être au format JPG, PNG ou WEBP.')
  }
  if (apres.value && !['image/jpeg', 'image/png', 'image/webp'].includes(apres.value.type)) {
    throw new Error('La photo après doit être au format JPG, PNG ou WEBP.')
  }
}
const publier=async()=>{erreur.value='';envoi.value=true;try{validerFormulaire();const donnees={titre:titre.value.trim(),description:description.value.trim(),specialite:specialite.value,photoAvant:avant.value,photoApres:apres.value};const resultat=props.realisation?await modifierRealisation(props.realisation.id,donnees):await ajouterRealisation(donnees);emit('publie',resultat)}catch(e){erreur.value=e.message}finally{envoi.value=false}}
</script>
<template><div class="voile" @click.self="emit('fermer')"><section class="modale" role="dialog" aria-modal="true"><header><h1>▣ {{ realisation ? 'Modifier la réalisation' : 'Ajouter une nouvelle réalisation' }}</h1><button @click="emit('fermer')">×</button></header><form @submit.prevent="publier"><label>Titre de la réparation *<input v-model.trim="titre" required maxlength="180" placeholder="Ex. Remplacement d’écran Samsung S21"></label><label>Spécialité associée *<select v-model="specialite" required><option value="" disabled>Choisissez une spécialité</option><option v-for="item in specialites" :key="item.id" :value="item.id">{{ item.nom }}</option></select></label><fieldset><legend>Photos avant / après <small>(facultatif — laissez vide pour conserver la photo actuelle)</small></legend><label class="upload">Photo avant<input type="file" accept="image/jpeg,image/png,image/webp" @change="fichier($event, 'avant')"><small>{{ avant?.name || 'Choisir une image' }}</small></label><label class="upload">Photo après<input type="file" accept="image/jpeg,image/png,image/webp" @change="fichier($event, 'apres')"><small>{{ apres?.name || 'Choisir une image' }}</small></label></fieldset><label>Description du travail effectué *<textarea v-model.trim="description" required maxlength="500" placeholder="Décrivez la panne, les étapes et le résultat final."></textarea></label><p v-if="erreur" class="erreur">{{ erreur }}</p><footer><button type="button" @click="emit('fermer')">Annuler</button><button class="publier" :disabled="envoi">{{ envoi ? (realisation ? 'Enregistrement…' : 'Publication…') : (realisation ? 'Enregistrer' : 'Publier') }}</button></footer></form></section></div></template>
<style scoped>.voile{position:fixed;z-index:30;inset:0;display:grid;place-items:center;padding:20px;background:#08275780;backdrop-filter:blur(2px)}.modale{width:min(625px,100%);border-radius:14px;background:#fff;color:#092d6a;box-shadow:0 20px 50px #041b4538}.modale>header{display:flex;align-items:center;justify-content:space-between;padding:25px 28px;border-bottom:1px solid #dce7f5}.modale h1{margin:0;font-size:21px}.modale>header button{border:0;background:transparent;color:#0d4288;font-size:28px}.modale form{padding:22px 28px}.modale label{display:grid;gap:8px;margin-bottom:18px;font-size:14px;font-weight:800}.modale input,.modale select,.modale textarea{width:100%;box-sizing:border-box;border:1px solid #b8d3fb;border-radius:9px;padding:12px;color:#153b78;font:400 14px Inter,Arial,sans-serif}.modale textarea{height:92px;resize:vertical}.modale fieldset{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin:0 0 18px;border:0;padding:0}.modale legend{grid-column:1/-1;margin-bottom:8px;font-size:14px;font-weight:800}.upload{min-height:85px;padding:12px;border:1px dashed #9cc8ff;border-radius:8px;background:#f9fcff}.upload input{padding:0;border:0;background:transparent;font-size:12px}.upload small{color:#6987b5;font-weight:400;overflow:hidden;text-overflow:ellipsis}.erreur{color:#d43b50;font-size:13px}.modale footer{display:flex;justify-content:flex-end;gap:12px}.modale footer button{height:44px;padding:0 20px;border:1px solid #b9d1f3;border-radius:8px;background:#fff;color:#48668e;font-weight:700}.modale footer .publier{border:0;background:#0e61dd;color:#fff}@media(max-width:500px){.modale form{padding:18px}.modale fieldset{grid-template-columns:1fr}}</style>
