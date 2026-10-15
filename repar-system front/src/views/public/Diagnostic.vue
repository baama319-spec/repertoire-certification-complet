<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import CarteProximite from '../../components/public/CarteProximite.vue'
import {
  analyserDiagnostic,
  chargerReferentielsDiagnostic,
  chargerReparateursProches,
  trouverSpecialite,
  traduireDescription,
  transcrireAudio,
} from '../../services/serviceDiagnostic'

const formulaire = ref({ materiel: 'Smartphone', modele: '', description: '', lieu: 'Dakar' })
const route = useRoute()
const analyseLancee = ref(false)
const analyseEnCours = ref(false)
const erreur = ref('')
const erreurVocale = ref('')
const enregistrementEnCours = ref(false)
const transcriptionEnCours = ref(false)
const traductionEnCours = ref(false)
const descriptionTraduite = ref(false)
const descriptionOriginale = ref('')
const diagnostic = ref(null)
const localisations = ref([])
const specialites = ref([])
const referentielsEnCours = ref(true)
const reparateurs = ref([])
const position = ref(null)
const localisationActive = ref(false)
const localisationErreur = ref('')
let enregistreurAudio = null
let fluxAudio = null
let minuterieEnregistrement = null

const villesDisponibles = computed(() => [...new Set(localisations.value.map((item) => item.ville).filter(Boolean))])
const specialiteSuggeree = computed(() => trouverSpecialite(specialites.value, diagnostic.value?.specialite))
const reparateursPourCarte = computed(() => reparateurs.value.map((reparateur) => {
  const utilisateur = reparateur.utilisateur_detail || {}
  const specialitesDuProfil = reparateur.specialites_detail || []
  const latitude = Number(reparateur.latitude)
  const longitude = Number(reparateur.longitude)
  return {
    id: reparateur.id,
    slug: String(reparateur.id),
    name: [utilisateur.prenom, utilisateur.nom].filter(Boolean).join(' ') || 'Réparateur vérifié',
    specialty: specialitesDuProfil.map((item) => item.nom).join(', ') || diagnostic.value?.specialite || 'Réparation',
    image: utilisateur.photo_profil,
    lat: Number.isFinite(latitude) ? latitude : null,
    lon: Number.isFinite(longitude) ? longitude : null,
    distanceKm: reparateur.distance_km,
  }
}))

const libererMicrophone = () => {
  if (minuterieEnregistrement) window.clearTimeout(minuterieEnregistrement)
  minuterieEnregistrement = null
  fluxAudio?.getTracks().forEach((piste) => piste.stop())
  fluxAudio = null
}

const arreterEnregistrement = () => {
  if (minuterieEnregistrement) window.clearTimeout(minuterieEnregistrement)
  minuterieEnregistrement = null
  if (enregistreurAudio && enregistreurAudio.state !== 'inactive') enregistreurAudio.stop()
  enregistrementEnCours.value = false
}

const demarrerEnregistrement = async () => {
  erreurVocale.value = ''
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    erreurVocale.value = 'L’enregistrement audio n’est pas pris en charge par ce navigateur. Vous pouvez saisir votre description au clavier.'
    return
  }

  try {
    fluxAudio = await navigator.mediaDevices.getUserMedia({ audio: true })
    const formats = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4']
    const mimeType = formats.find((format) => window.MediaRecorder.isTypeSupported(format))
    enregistreurAudio = new window.MediaRecorder(fluxAudio, mimeType ? { mimeType } : undefined)
    const morceaux = []
    enregistreurAudio.ondataavailable = (event) => {
      if (event.data.size) morceaux.push(event.data)
    }
    enregistreurAudio.onerror = () => {
      erreurVocale.value = 'Une erreur est survenue pendant l’enregistrement. Réessayez ou saisissez le texte.'
      enregistrementEnCours.value = false
      libererMicrophone()
    }
    enregistreurAudio.onstop = async () => {
      libererMicrophone()
      const audio = new Blob(morceaux, { type: enregistreurAudio.mimeType || 'audio/webm' })
      if (!audio.size) {
        erreurVocale.value = 'Aucune voix détectée. Réessayez ou saisissez le texte.'
        return
      }
      if (audio.size > 20 * 1024 * 1024) {
        erreurVocale.value = 'L’enregistrement dépasse la limite de 20 Mo. Faites une prise plus courte.'
        return
      }
      transcriptionEnCours.value = true
      try {
        const resultat = await transcrireAudio(audio)
        formulaire.value.description = resultat.text
        descriptionTraduite.value = false
        descriptionOriginale.value = ''
      } catch (error) {
        erreurVocale.value = error.message
      } finally {
        transcriptionEnCours.value = false
      }
    }
    enregistreurAudio.start()
    enregistrementEnCours.value = true
    minuterieEnregistrement = window.setTimeout(arreterEnregistrement, 120000)
  } catch (error) {
    libererMicrophone()
    erreurVocale.value = error.name === 'NotAllowedError'
      ? 'Autorisez l’accès au microphone pour enregistrer votre description.'
      : 'Impossible d’accéder au microphone. Vérifiez les autorisations ou saisissez le texte.'
  }
}

onBeforeUnmount(() => {
  if (enregistreurAudio && enregistreurAudio.state !== 'inactive') {
    enregistreurAudio.onstop = null
    enregistreurAudio.stop()
  }
  libererMicrophone()
})

const chargerRecommandations = async () => {
  if (!position.value || !diagnostic.value) return
  try {
    reparateurs.value = await chargerReparateursProches({
      ...position.value,
      specialite: specialiteSuggeree.value?.id,
    })
  } catch (error) {
    localisationErreur.value = error.message
  }
}

const activerLocalisation = () => {
  localisationErreur.value = ''
  if (!navigator.geolocation) {
    localisationErreur.value = 'La géolocalisation n’est pas disponible sur cet appareil.'
    return
  }
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      position.value = { latitude: coords.latitude, longitude: coords.longitude }
      localisationActive.value = true
      await chargerRecommandations()
    },
    () => {
      localisationErreur.value = 'Autorisez la localisation pour voir les réparateurs les plus proches.'
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
  )
}

const validerDiagnostic = () => {
  const description = formulaire.value.description.trim()
  if (!formulaire.value.materiel) throw new Error('Veuillez sélectionner un type d’appareil.')
  if (description.length < 10) throw new Error('La description du problème doit contenir au moins 10 caractères.')
  if (!String(formulaire.value.lieu || '').trim()) throw new Error('Veuillez sélectionner une ville.')
}

const lancerAnalyse = async () => {
  erreur.value = ''
  if (traductionEnCours.value) return
  analyseEnCours.value = true
  try {
    validerDiagnostic()
    if (!descriptionTraduite.value) {
      traductionEnCours.value = true
      descriptionOriginale.value = formulaire.value.description.trim()
      const resultatTraduction = await traduireDescription(descriptionOriginale.value)
      formulaire.value.description = resultatTraduction.description_francaise
      descriptionTraduite.value = true
      return
    }
    diagnostic.value = await analyserDiagnostic({
      appareil: formulaire.value.materiel,
      marque: formulaire.value.modele,
      description: formulaire.value.description.trim(),
      ville: formulaire.value.lieu,
    })
    sessionStorage.setItem('reparsystem-diagnostic', JSON.stringify({
      resultat: diagnostic.value,
      specialiteId: specialiteSuggeree.value?.id || null,
    }))
    analyseLancee.value = true
    await chargerRecommandations()
  } catch (error) {
    erreur.value = error.message
  } finally {
    analyseEnCours.value = false
    traductionEnCours.value = false
  }
}

const restaurerDescriptionOriginale = () => {
  formulaire.value.description = descriptionOriginale.value
  descriptionTraduite.value = false
  descriptionOriginale.value = ''
  erreur.value = ''
}

const recommencer = () => {
  analyseLancee.value = false
  diagnostic.value = null
  reparateurs.value = []
  position.value = null
  localisationActive.value = false
  erreur.value = ''
  erreurVocale.value = ''
  descriptionOriginale.value = ''
  descriptionTraduite.value = false
}

onMounted(async () => {
  try {
    const referentiels = await chargerReferentielsDiagnostic()
    localisations.value = referentiels.localisations
    specialites.value = referentiels.specialites
    if (!villesDisponibles.value.includes(formulaire.value.lieu) && villesDisponibles.value.length) {
      formulaire.value.lieu = villesDisponibles.value[0]
    }
  } catch (error) {
    erreur.value = error.message
  } finally {
    referentielsEnCours.value = false
  }
})
</script>

<template>
  <div class="home-page"><EntetePublic /></div>
  <main>
    <section class="workspace" aria-label="Formulaire de diagnostic">
      <div v-if="!analyseLancee" class="form-card">
        <div class="card-heading"><div><h2>Parlez-nous de votre appareil</h2><p>Expliquez la panne comme vous le souhaitez.</p></div></div>
        <p v-if="route.query.reparateur" class="field-hint">Votre demande sera transmise au réparateur dont vous consultez le profil.</p>
        <div class="field-block">
          <label>De quel appareil s’agit-il ?</label>
          <div class="choice-grid">
            <button v-for="type in ['Smartphone', 'Ordinateur', 'Tablette', 'Télévision']" :key="type" type="button" :class="['choice', { selected: formulaire.materiel === type }]" @click="formulaire.materiel = type">{{ type }}</button>
          </div>
        </div>
        <div class="field-block"><label for="modele">Marque et modèle <small>(facultatif)</small></label><input id="modele" v-model.trim="formulaire.modele" maxlength="80" placeholder="Ex. Samsung Galaxy S21"></div>
        <div class="field-block">
          <div class="description-label-row"><label for="description">Que se passe-t-il ?</label><button class="voice-action" type="button" :disabled="transcriptionEnCours" :aria-pressed="enregistrementEnCours" @click="enregistrementEnCours ? arreterEnregistrement() : demarrerEnregistrement()">{{ enregistrementEnCours ? 'Arrêter l’enregistrement' : transcriptionEnCours ? 'Transcription en cours…' : 'Décrire à voix haute' }}</button></div>
          <textarea id="description" v-model.trim="formulaire.description" placeholder="Ex. : mon téléphone est tombé, l’écran s’allume mais le tactile ne répond plus…" rows="5"></textarea>
          <span class="field-hint">Saisissez ou dictez votre description en français, en wolof ou en mélangeant les deux. Gemini la traduira en français avant le diagnostic.</span>
          <div v-if="descriptionTraduite" class="translation-review"><strong>Traduction française — vérifiez-la avant le diagnostic</strong><p v-if="descriptionOriginale">Texte original : {{ descriptionOriginale }}</p><button type="button" class="restore-description" @click="restaurerDescriptionOriginale">Revenir au texte original</button></div>
          <p v-if="enregistrementEnCours" class="voice-status" aria-live="polite">Enregistrement en cours — appuyez sur « Arrêter » quand vous avez terminé (2 min maximum).</p>
          <p v-else-if="transcriptionEnCours" class="voice-status" aria-live="polite">Transcription automatique de votre audio…</p>
          <p v-if="erreurVocale" class="error-message" role="alert">{{ erreurVocale }}</p>
        </div>
        <div class="field-block"><label for="lieu">Où êtes-vous ?</label><select id="lieu" v-model="formulaire.lieu"><option v-for="ville in villesDisponibles" :key="ville" :value="ville">{{ ville }}</option></select></div>
        <p v-if="erreur" class="error-message" role="alert">{{ erreur }}</p>
        <p v-if="referentielsEnCours" class="field-hint">Chargement des zones d’intervention…</p>
        <button class="main-action" type="button" :disabled="analyseEnCours || traductionEnCours || enregistrementEnCours || transcriptionEnCours || formulaire.description.trim().length < 10" @click="lancerAnalyse">{{ traductionEnCours ? 'Traduction en français…' : analyseEnCours ? 'Analyse en cours…' : descriptionTraduite ? 'Lancer mon diagnostic IA' : 'Traduire en français et vérifier' }} <AppIcon name="arrow-right" :size="18" /></button>
        <p class="privacy-note">L’audio est transcrit puis la description, originale ou saisie, est traduite en français par Gemini. Vérifiez la traduction avant le diagnostic.</p>
      </div>

      <div v-else class="results-stack">
        <section class="result-card diagnostic-section">
          <div class="result-topline"><span class="result-status">Analyse terminée</span></div>
          <h2>Résultat de votre pré-diagnostic</h2>
          <div class="answer-grid">
            <div class="answer answer-main"><span>Causes possibles</span><strong>{{ diagnostic.causes_possibles?.join(', ') || diagnostic.probleme_probable || 'À préciser' }}</strong><p>Cette hypothèse doit être confirmée par un réparateur.</p></div>
            <div class="answer answer-advice"><span>Conseils à suivre</span><ul v-if="diagnostic.conseils_securite?.length"><li v-for="(conseil, index) in diagnostic.conseils_securite" :key="index">{{ conseil }}</li></ul><p v-else>Éteignez l’appareil si possible et consultez un réparateur qualifié.</p></div>
            <div class="answer"><span>Qui consulter ?</span><strong>{{ diagnostic.specialite || 'Un réparateur qualifié' }}</strong><p>Pour confirmer la panne et vous guider dans la réparation.</p></div>
          </div>
          <p class="result-specialty">Spécialité suggérée : {{ diagnostic.specialite || 'Réparation' }} · {{ diagnostic.categorie || 'Diagnostic' }}</p>
          <div v-if="diagnostic.questions_a_poser?.length" class="questions"><strong>Pour affiner le diagnostic</strong><ul><li v-for="question in diagnostic.questions_a_poser" :key="question">{{ question }}</li></ul></div>
          <p v-if="diagnostic.avertissement" class="disclaimer">{{ diagnostic.avertissement }}</p>
        </section>
        <section class="recommendations">
          <div class="recommendation-heading"><h2>Les réparateurs pour vous aider</h2><button v-if="!localisationActive" class="location-primary" type="button" @click="activerLocalisation">Activer ma localisation <AppIcon name="locate" :size="16" /></button></div>
          <p v-if="localisationErreur" class="error-message" role="alert">{{ localisationErreur }}</p>
          <p v-else-if="!localisationActive" class="location-help">Activez votre position pour voir les professionnels compatibles les plus proches.</p>
          <p v-else-if="!reparateurs.length" class="location-help">Aucun réparateur vérifié et géolocalisé ne correspond encore à cette spécialité.</p>
          <CarteProximite v-else class="diagnostic-map" :professionals="reparateursPourCarte" :initial-position="position" :auto-locate="false" />
        </section>
        <p v-if="erreur" class="error-message" role="alert">{{ erreur }}</p>
        <button class="restart-action" type="button" @click="recommencer">Recommencer un diagnostic</button>
      </div>
    </section>
  </main>
  <PiedDePage />
</template>

<style scoped>
.home-page :deep(.header) { background: #0b1427; color: #fff; }
.home-page :deep(.header a) { color: #fff; }
main { min-height: 70vh; padding: 20px 0 64px; background: radial-gradient(ellipse at 50% 0%, #214767, #102c49 55%, #0b2038); color: #102b3b; }
.workspace { width: min(calc(100% - 40px), 900px); margin: 0 auto; }
.form-card, .result-card, .recommendations { padding: clamp(24px, 5vw, 44px); border: 1px solid #e3ebe8; border-radius: 18px; background: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.15); }
.card-heading h2, .result-card h2, .recommendation-heading h2 { margin: 0 0 8px; color: #102b3b; font-size: clamp(23px, 3vw, 31px); }
.card-heading p, .field-hint, .privacy-note, .location-help { color: #718788; font-size: 12px; line-height: 1.55; }
.field-block { margin: 26px 0; }
.field-block > label, .description-label-row > label { display: block; margin-bottom: 11px; color: #284750; font-size: 13px; font-weight: 800; }
.field-block small { color: #819596; font-weight: 400; }
.choice-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.choice { min-height: 64px; border: 1px solid #dbe7e4; border-radius: 10px; background: #fbfdfc; color: #526f70; font: inherit; cursor: pointer; }
.choice.selected, .choice:hover { border-color: #168273; background: #eef9f5; color: #087f70; }
.field-block input, .field-block textarea, .field-block select { width: 100%; box-sizing: border-box; border: 1px solid #dbe7e4; border-radius: 10px; padding: 14px; background: #fbfdfc; color: #284750; font: inherit; font-size: 14px; }
.field-block textarea { resize: vertical; }
.field-block input:focus, .field-block textarea:focus, .field-block select:focus { outline: 2px solid #168273; outline-offset: 1px; }
.description-label-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.voice-action, .location-primary, .restart-action { padding: 11px 14px; border: 1px solid #b8d8d0; border-radius: 9px; background: #f2faf7; color: #087f70; font: inherit; font-size: 12px; font-weight: 800; cursor: pointer; }
.voice-action:disabled { opacity: .65; cursor: wait; }
.voice-action[aria-pressed="true"] { border-color: #b43c46; background: #fff0f0; color: #a8323b; }
.voice-status { color: #168273; font-size: 12px; }
.translation-review { margin-top: 10px; padding: 12px 14px; border-left: 3px solid #168273; border-radius: 0 8px 8px 0; background: #eef8f5; color: #365d5a; font-size: 12px; line-height: 1.5; }
.translation-review p { margin: 5px 0; overflow-wrap: anywhere; color: #687f7e; }
.restore-description { padding: 0; border: 0; background: transparent; color: #087f70; font: inherit; font-size: 11px; font-weight: 800; text-decoration: underline; cursor: pointer; }
.main-action { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; margin-top: 18px; padding: 16px; border: 0; border-radius: 10px; background: #168273; color: white; font: inherit; font-weight: 800; cursor: pointer; }
.main-action:disabled { opacity: .5; cursor: not-allowed; }
.privacy-note { margin: 14px 0 0; text-align: center; }
.error-message { padding: 12px 14px; border-radius: 8px; background: #fff0f0; color: #a8323b; font-size: 12px; }
.results-stack { display: grid; gap: 18px; }
.result-topline { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #edf2f0; color: #168273; font-size: 12px; font-weight: 800; }
.answer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 24px 0; }
.answer { padding: 17px; border-radius: 12px; background: #f5faf8; }
.answer-main { background: #e9f7f1; }
.answer span { display: block; margin-bottom: 10px; color: #168273; font-size: 11px; font-weight: 800; }
.answer strong { color: #234653; font-size: 14px; line-height: 1.5; }
.answer p, .answer li, .questions li, .disclaimer { color: #627d7d; font-size: 12px; line-height: 1.6; }
.answer ul, .questions ul { padding-left: 18px; }
.result-specialty { color: #668080; font-size: 13px; }
.questions { margin: 18px 0; padding: 16px; border-left: 3px solid #e79b55; background: #fff9f1; }
.recommendation-heading { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.recommendation-heading h2 { font-size: 22px; }
.location-help { margin-bottom: 0; }
.diagnostic-map :deep(.proximity-section) { width: 100%; padding: 0; background: transparent; }
.diagnostic-map :deep(.proximity-layout) { width: 100%; margin: 0; }
.restart-action { display: block; margin: 0 auto; background: #fff; }
@media (max-width: 650px) { .workspace { width: min(calc(100% - 24px), 900px); }.choice-grid, .answer-grid { grid-template-columns: repeat(2, 1fr); }.recommendation-heading { align-items: flex-start; flex-direction: column; }.voice-action { white-space: nowrap; } }
@media (max-width: 420px) { .choice-grid, .answer-grid { grid-template-columns: 1fr; }.description-label-row { align-items: flex-start; flex-direction: column; }.voice-action { width: 100%; } }
</style>
