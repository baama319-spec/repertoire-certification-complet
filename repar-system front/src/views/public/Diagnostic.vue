<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import CarteProximite from '../../components/public/CarteProximite.vue'
import { RouterLink } from 'vue-router'
import {
  analyserDiagnostic,
  chargerReferentielsDiagnostic,
  chargerReparateursProches,
  trouverSpecialite,
} from '../../services/serviceDiagnostic'

const formulaire = ref({ materiel: 'Smartphone', modele: '', description: '', lieu: 'Dakar' })
const route = useRoute()
const analyseLancee = ref(false)
const analyseEnCours = ref(false)
const erreur = ref('')
const diagnostic = ref(null)
const localisations = ref([])
const specialites = ref([])
const referentielsEnCours = ref(true)
const reparateurs = ref([])
const position = ref(null)
const localisationEnCours = ref(false)
const localisationActive = ref(false)
const localisationErreur = ref('')
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

const confiance = computed(() => `${Math.round((Number(diagnostic.value?.confiance) || 0) * 100)}%`)
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
  localisationEnCours.value = true
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      position.value = { latitude: coords.latitude, longitude: coords.longitude }
      localisationActive.value = true
      localisationEnCours.value = false
      await chargerRecommandations()
    },
    () => {
      localisationEnCours.value = false
      localisationErreur.value = 'Autorisez la localisation pour voir les réparateurs les plus proches.'
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
  )
}

const validerDiagnostic = () => {
  const description = formulaire.value.description.trim()
  if (!formulaire.value.materiel) {
    throw new Error('Veuillez sélectionner un type d’appareil.')
  }
  if (!description || description.length < 10) {
    throw new Error('La description du problème doit contenir au moins 10 caractères.')
  }
  if (!formulaire.value.lieu || !String(formulaire.value.lieu).trim()) {
    throw new Error('Veuillez sélectionner une ville.')
  }
}

const lancerAnalyse = async () => {
  erreur.value = ''
  analyseEnCours.value = true
  try {
    validerDiagnostic()
    diagnostic.value = await analyserDiagnostic({
      appareil: formulaire.value.materiel,
      description: formulaire.value.description.trim(),
      ville: formulaire.value.lieu,
    })
    analyseLancee.value = true
    await chargerRecommandations()
  } catch (error) {
    erreur.value = error.message
  } finally {
    analyseEnCours.value = false
  }
}

const recommencer = () => {
  analyseLancee.value = false
  diagnostic.value = null
  reparateurs.value = []
  position.value = null
  localisationActive.value = false
  erreur.value = ''
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
        <div class="card-heading"><div><h2>Parlez-nous de votre appareil</h2></div></div>
        <p v-if="route.query.reparateur" class="field-hint">Votre demande sera transmise au réparateur dont vous consultez le profil.</p>
        <div class="field-block"><label>De quel appareil s’agit-il ?</label><div class="choice-grid"><button v-for="type in ['Smartphone', 'Ordinateur', 'Tablette', 'Télévision']" :key="type" type="button" :class="['choice', { selected: formulaire.materiel === type }]" @click="formulaire.materiel = type"><span class="choice-icon">{{ type === 'Smartphone' ? '▯' : type === 'Ordinateur' ? '▱' : type === 'Tablette' ? '▯' : '▭' }}</span>{{ type }}</button></div></div>
        <div class="field-block"><label for="modele">Marque et modèle <small>(facultatif)</small></label><input id="modele" v-model.trim="formulaire.modele" maxlength="80" placeholder="Ex. Samsung Galaxy S21"></div>
        <div class="field-block"><label for="description">Que se passe-t-il ?</label><textarea id="description" v-model.trim="formulaire.description" placeholder="Exemple : mon téléphone est tombé, l’écran s’allume mais le tactile ne répond plus..." rows="5"></textarea><span class="field-hint">Décrivez les symptômes, même simplement. Minimum 10 caractères.</span></div>
        <div class="details-row location-only"><div class="field-block"><label for="lieu">Où êtes-vous ?</label><select id="lieu" v-model="formulaire.lieu"><option v-for="ville in villesDisponibles" :key="ville" :value="ville">{{ ville }}</option></select></div></div>
        <p v-if="localisationErreur" class="error-message" role="alert">{{ localisationErreur }}</p>
        <p v-if="erreur" class="error-message" role="alert">{{ erreur }}</p>
        <p v-if="referentielsEnCours" class="field-hint">Chargement des zones d’intervention…</p>
        <button class="main-action" type="button" :disabled="analyseEnCours || formulaire.description.length < 10" @click="lancerAnalyse">{{ analyseEnCours ? 'Analyse en cours…' : 'Lancer mon diagnostic IA' }} <span>→</span></button>
        <RouterLink class="diagnostic-action" :to="{ name: 'demande-reparation', query: route.query.reparateur ? { reparateur: route.query.reparateur } : {} }">Demander une intervention sans diagnostic</RouterLink>
        <p class="privacy-note">Vos informations restent privées et servent uniquement à vous orienter.</p>
      </div>

      <div v-else class="results-stack">
        <section class="result-card diagnostic-section">
        <div class="result-topline"><span class="result-status">Analyse terminée</span></div>
        <div class="result-heading"><div><h2>{{ diagnostic.probleme_probable }}</h2><p class="result-specialty">Spécialité suggérée : {{ diagnostic.specialite }} · {{ diagnostic.categorie }}</p></div><div class="confidence"><strong>{{ confiance }}</strong><span>de confiance</span></div></div>
        <div class="answer-grid"><div class="answer answer-main"><span>Causes possibles</span><strong>{{ diagnostic.causes_possibles.join(', ') || 'À préciser' }}</strong><p>Cette hypothèse doit être confirmée par un réparateur.</p></div><div class="answer"><span>Niveau d’urgence</span><strong>{{ diagnostic.niveau_urgence }}</strong><p>Suivez les conseils de sécurité avant toute manipulation.</p></div><div class="answer"><span>Sécurité</span><strong>{{ diagnostic.conseils_securite[0] || 'Faites vérifier l’appareil.' }}</strong></div></div>
        <div v-if="diagnostic.questions_a_poser.length" class="questions"><span class="kicker">POUR AFFINER LE DIAGNOSTIC</span><ul><li v-for="question in diagnostic.questions_a_poser" :key="question">{{ question }}</li></ul></div>
        </section>
        <section class="recommendations"><div class="recommendation-heading"><div><span class="kicker">ÉTAPE SUIVANTE</span><h2>Les réparateurs pour vous aider</h2><p>Une sélection basée sur votre diagnostic et votre position.</p></div><button v-if="!localisationActive" class="location-primary" type="button" @click="activerLocalisation">Activer ma localisation <span>⌖</span></button></div><p v-if="localisationErreur" class="error-message" role="alert">{{ localisationErreur }}</p><p v-else-if="!localisationActive" class="location-help">Activez votre position pour voir les professionnels compatibles les plus proches.</p><p v-else-if="!reparateurs.length" class="location-help">Aucun réparateur vérifié et géolocalisé ne correspond encore à cette spécialité.</p><CarteProximite v-else class="diagnostic-map" :professionals="reparateursPourCarte" :initial-position="position" :auto-locate="false" /></section>
        <section class="result-actions">
        <p v-if="erreur" class="error-message" role="alert">{{ erreur }}</p>
        <RouterLink class="main-action request-link" :to="{ name: 'demande-reparation', query: route.query.reparateur ? { reparateur: route.query.reparateur } : {} }">Faire une demande d’intervention <span>→</span></RouterLink>
        <button class="restart-action" type="button" @click="recommencer">Recommencer un diagnostic</button>
        </section>
      </div>
    </section>

  </main>
  <PiedDePage />
</template>

<style scoped>
.home-page :deep(.header) { background: #0b1427; color: #fff; border-bottom-color: rgba(255,255,255,.12); }
.home-page :deep(.header a) { color: #fff; }
.home-page :deep(.header .logo-reparsystem) { background: #fff; border-radius: 8px; padding: 3px; }
.home-page :deep(.header .signup) { background: #087f70; color: #fff; }
main { background: #f7f8f5; color: #102b3b; }
.field-block input { width: 100%; box-sizing: border-box; border: 1px solid #dbe7e4; border-radius: 10px; padding: 14px; color: #284750; background: #fbfdfc; font: inherit; font-size: 13px; outline: none; }
.field-block input:focus { border-color: #168273; }
.diagnostic-action { display: block; margin: 15px auto 0; padding: 8px 12px; border: 0; background: transparent; color: #168273; font: inherit; font-size: 12px; font-weight: 700; cursor: pointer; }
.request-link { display: block; text-align: center; text-decoration: none; box-sizing: border-box; }
.diagnostic-action:disabled { opacity: .55; cursor: wait; }
.success-message { margin: 14px 0; padding: 13px 16px; border-radius: 9px; background: #e9f7f1; color: #147665; font-size: 13px; line-height: 1.5; }
.intro { min-height: 430px; padding: 78px max(9vw, 32px) 58px; background: #dcefe9; display: flex; justify-content: space-between; align-items: center; overflow: hidden; }
.intro-copy { max-width: 650px; position: relative; z-index: 1; }
.kicker { color: #168273; font-size: 10px; font-weight: 800; letter-spacing: 1.6px; }
h1, h2, h3, p { margin-top: 0; }
.intro h1 { margin: 17px 0; color: #102b3b; font-size: clamp(40px, 6vw, 76px); line-height: .98; letter-spacing: -3px; }
.intro h1 em { color: #168273; font-family: Georgia, serif; font-weight: 400; }
.intro p { max-width: 470px; color: #56727a; font-size: 15px; line-height: 1.7; }
.intro-orbit { width: 310px; height: 310px; margin-right: 7%; position: relative; flex: 0 0 auto; }
.orbit-ring { position: absolute; inset: 0; border: 1px solid rgba(22,130,115,.28); border-radius: 50%; transform: rotate(-20deg) skew(-8deg); }
.ring-two { inset: 36px -22px; transform: rotate(34deg) skew(12deg); border-color: rgba(22,130,115,.18); }
.orbit-core { width: 84px; height: 84px; position: absolute; top: 113px; left: 113px; display: grid; place-items: center; border-radius: 50%; background: #fff; color: #e79b55; box-shadow: 0 15px 38px rgba(34,97,92,.16); font-size: 31px; }
.orbit-label { position: absolute; padding: 9px 12px; border-radius: 10px; background: rgba(255,255,255,.82); color: #39706f; font-size: 10px; font-weight: 700; box-shadow: 0 6px 16px rgba(34,97,92,.08); }.label-one { top: 42px; right: -9px; }.label-two { bottom: 38px; left: -12px; }
.workspace { width: min(100% - 48px, 1440px); margin: 0 auto; padding: 58px 0 78px; position: relative; z-index: 2; }.progress-line { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 20px; color: #799096; font-size: 11px; }.progress-step b { margin-right: 6px; color: #a7b5b4; }.progress-step.active { color: #168273; font-weight: 800; }.progress-step.active b { color: #168273; }.progress-bar { width: 95px; height: 1px; background: #c4d4d1; }
.form-card, .result-card { padding: 48px 64px; background: #fff; border: 1px solid #e3ebe8; border-radius: 20px; box-shadow: 0 20px 50px rgba(21,70,74,.09); }.card-heading { display: flex; gap: 16px; align-items: flex-start; margin-bottom: 37px; }.step-tag { width: 32px; height: 32px; display: grid; place-items: center; flex: 0 0 auto; border-radius: 50%; background: #e7f5f0; color: #168273; font-size: 10px; font-weight: 800; }.card-heading h2, .result-heading h2 { margin: 0 0 7px; color: #102b3b; font-size: 27px; letter-spacing: -.7px; }.card-heading p { margin: 0; color: #809195; font-size: 13px; }
.field-block { margin-bottom: 27px; }.field-block > label:first-child { display: block; margin-bottom: 11px; color: #284750; font-size: 12px; font-weight: 800; }.choice-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 9px; }.choice { border: 1px solid #e1eae7; border-radius: 10px; padding: 14px 8px; color: #678085; background: #fbfcfb; font: inherit; font-size: 11px; cursor: pointer; transition: .2s ease; }.choice:hover, .choice.selected { border-color: #168273; background: #eef9f5; color: #168273; }.choice-icon { display: block; margin-bottom: 7px; font-size: 23px; }.field-block textarea, select { width: 100%; box-sizing: border-box; border: 1px solid #dbe7e4; border-radius: 10px; padding: 14px; color: #284750; background: #fbfdfc; font: inherit; font-size: 13px; outline: none; resize: vertical; }.field-block textarea:focus, select:focus { border-color: #168273; }.field-hint { display: block; margin-top: 8px; color: #9aa9aa; font-size: 10px; }.details-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }.field-block small { margin-left: 5px; color: #a5b2b1; font-weight: 400; }.photo-button { display: flex; align-items: center; justify-content: space-between; min-height: 17px; padding: 12px 14px; border: 1px dashed #a7cbc2; border-radius: 10px; color: #168273; font-size: 12px; cursor: pointer; }.photo-button span { font-size: 20px; font-weight: 300; }.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }.photo-preview { width: 70px; height: 70px; margin: -10px 0 20px; object-fit: cover; border-radius: 10px; }.main-action { width: 100%; padding: 16px 20px; border: 0; border-radius: 10px; background: #168273; color: #fff; font: inherit; font-size: 13px; font-weight: 800; cursor: pointer; transition: .2s ease; }.main-action:hover { background: #0d685e; transform: translateY(-2px); }.main-action span { margin-left: 10px; font-size: 19px; }.privacy-note { margin: 14px 0 0; text-align: center; color: #9ba9a8; font-size: 10px; }
.result-topline, .result-heading, .match-heading { display: flex; justify-content: space-between; gap: 20px; align-items: center; }.result-status { color: #168273; font-size: 11px; font-weight: 800; }.result-heading { align-items: flex-end; margin: 25px 0 32px; }.result-heading h2 { max-width: 580px; font-size: 35px; line-height: 1.08; }.confidence { display: grid; text-align: right; color: #168273; }.confidence strong { font-size: 31px; }.confidence span { color: #839394; font-size: 10px; }.answer-grid { display: grid; grid-template-columns: 1.3fr 1fr 1fr; gap: 10px; margin-bottom: 42px; }.answer { min-height: 116px; padding: 17px; border-radius: 12px; background: #f5faf8; }.answer-main { background: #e9f7f1; }.answer span { display: block; margin-bottom: 13px; color: #168273; font-size: 10px; font-weight: 800; }.answer strong { display: block; color: #234653; font-size: 13px; line-height: 1.35; }.answer p { margin: 9px 0 0; color: #799092; font-size: 10px; line-height: 1.4; }.match-heading { margin-bottom: 17px; }.match-heading h3 { margin: 7px 0 0; color: #24434c; font-size: 19px; }.text-action { border: 0; color: #168273; background: transparent; font: inherit; font-size: 11px; font-weight: 800; cursor: pointer; }.pro-list { border-top: 1px solid #e5ece9; }.pro-row { display: grid; grid-template-columns: 38px 1fr auto auto; align-items: center; gap: 12px; padding: 14px 0; border-bottom: 1px solid #e5ece9; }.avatar { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 50%; color: #fff; background: #3f8f87; font-weight: 800; }.pro-name { display: grid; gap: 4px; }.pro-name strong { color: #284750; font-size: 12px; }.pro-name span, .pro-rating { color: #879898; font-size: 10px; }.pro-rating { color: #d58b36; text-align: right; }.pro-rating small { display: block; margin-top: 4px; color: #91a09f; }.contact-action, .restart-action { padding: 9px 13px; border: 1px solid #b8d8d0; border-radius: 7px; background: #fff; color: #168273; font: inherit; font-size: 10px; font-weight: 800; cursor: pointer; }.restart-action { display: block; margin: 28px auto 0; border-color: transparent; background: #eef8f5; }.promise { padding: 75px 24px 105px; text-align: center; background: #fff; }.promise h2 { margin: 14px 0 34px; color: #102b3b; font-size: clamp(30px, 4vw, 47px); line-height: 1.05; letter-spacing: -1.5px; }.promise-points { display: flex; justify-content: center; gap: 44px; color: #7a8c8d; font-size: 11px; }.promise-points b { margin-right: 7px; color: #168273; }
@media (max-width: 720px) { .workspace { width: auto; margin: 0 14px; padding: 38px 0 55px; }.form-card, .result-card { padding: 28px 20px; }.choice-grid { grid-template-columns: repeat(2, 1fr); }.details-row, .answer-grid { grid-template-columns: 1fr; gap: 0; }.result-heading { align-items: flex-start; flex-direction: column; }.confidence { text-align: left; }.pro-row { grid-template-columns: 38px 1fr auto; }.contact-action { grid-column: 2 / -1; justify-self: start; }.promise-points { flex-direction: column; gap: 15px; }.progress-line { justify-content: flex-start; }.progress-bar { width: 35px; } }
.text-only-note { min-height: 48px; padding: 12px 14px; border: 1px solid #dbe7e4; border-radius: 10px; background: #f5faf8; color: #678085; font-size: 11px; }.text-only-note strong, .text-only-note span { display: block; }.text-only-note strong { margin-bottom: 5px; color: #168273; }.text-only-note span { line-height: 1.4; }.result-specialty { color: #799092; font-size: 12px; }.questions { margin-bottom: 20px; padding: 15px 17px; border-left: 3px solid #e79b55; background: #fff9f1; }.questions ul { margin: 10px 0 0; padding-left: 18px; color: #6f7774; font-size: 12px; line-height: 1.7; }.disclaimer { margin: 16px 0; color: #7d8c8a; font-size: 11px; line-height: 1.5; }.error-message, .success-message { margin: 14px 0; padding: 11px 13px; border-radius: 8px; font-size: 12px; line-height: 1.4; }.error-message { background: #fff0f0; color: #b43c46; }.success-message { background: #e9f7f1; color: #147665; }
.location-action { display: block; margin: 8px 0 6px; padding: 0; border: 0; background: transparent; color: #168273; font: inherit; font-size: 11px; font-weight: 800; cursor: pointer; }.location-action:disabled { opacity: .6; cursor: wait; }.location-help { margin: 0 0 18px; color: #849492; font-size: 11px; line-height: 1.5; }.recommendations { margin: 24px 0; padding-top: 20px; border-top: 1px solid #e5ece9; }
.diagnostic-map :deep(.proximity-section) { padding: 25px 0 0; background: transparent; }.diagnostic-map :deep(.proximity-heading) { margin-bottom: 16px; }.diagnostic-map :deep(.proximity-heading h2) { font-size: 21px; }.diagnostic-map :deep(.proximity-layout) { min-height: 430px; grid-template-columns: 155px minmax(260px, 1fr) 220px; }.diagnostic-map :deep(.senegal-map) { min-height: 430px; }.diagnostic-map :deep(.nearby-list) { padding: 12px 9px; }.diagnostic-map :deep(.nearby-card) { padding: 8px; }.diagnostic-map :deep(.nearby-card img) { width: 32px; height: 32px; }.diagnostic-map :deep(.nearby-actions) { display: grid; gap: 4px; justify-items: end; }.diagnostic-map :deep(.profile-link) { color: #087f70; font-size: 8px; font-weight: 800; white-space: nowrap; }
.workspace { width: min(100% - 56px, 1180px); padding-top: 42px; }.form-card, .result-card { padding: 38px 46px; border-radius: 16px; box-shadow: 0 18px 45px rgba(21,70,74,.08); animation: page-enter .55s cubic-bezier(.2,.75,.25,1) both; }.progress-line { margin-bottom: 16px; }.result-card { overflow: hidden; }.result-topline { padding-bottom: 4px; border-bottom: 1px solid #edf2f0; }.result-heading { margin: 26px 0 28px; }.result-heading h2 { max-width: 680px; font-size: clamp(29px, 3vw, 40px); letter-spacing: -1.2px; }.confidence { min-width: 92px; padding: 11px 14px; border-radius: 12px; background: #f0faf7; }.confidence strong { font-size: 27px; }.answer-grid { gap: 14px; margin-bottom: 30px; }.answer { min-height: 105px; padding: 16px; border: 1px solid #edf3f0; transition: transform .22s ease, box-shadow .22s ease; animation: answer-enter .5s ease both; }.answer:nth-child(2) { animation-delay: .08s; }.answer:nth-child(3) { animation-delay: .16s; }.answer:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(26,92,82,.08); }.questions { margin-bottom: 18px; border-radius: 0 10px 10px 0; animation: answer-enter .5s .2s ease both; }.recommendations { margin-top: 20px; }.diagnostic-map :deep(.proximity-section) { padding-top: 18px; }.diagnostic-map :deep(.proximity-layout) { min-height: 390px; grid-template-columns: 145px minmax(280px, 1fr) 230px; border-radius: 14px; }.diagnostic-map :deep(.senegal-map) { min-height: 390px; }.diagnostic-map :deep(.proximity-heading h2) { margin-top: 5px; font-size: 20px; }.diagnostic-map :deep(.proximity-heading p) { font-size: 11px; }.main-action { border-radius: 9px; box-shadow: 0 9px 18px rgba(22,130,115,.16); }.main-action:hover { box-shadow: 0 13px 24px rgba(22,130,115,.22); }.restart-action { transition: background .2s ease, transform .2s ease; }.restart-action:hover { transform: translateY(-2px); background: #e3f5ef; }.error-message, .success-message { animation: answer-enter .35s ease both; }
@keyframes page-enter { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } } @keyframes answer-enter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) { .form-card, .result-card, .answer, .questions, .error-message, .success-message { animation: none; transition: none; } }
@media (max-width: 720px) { .workspace { width: auto; margin: 0 14px; padding: 38px 0 55px; }.form-card, .result-card { padding: 28px 20px; }.result-heading h2 { font-size: 30px; }.confidence { padding: 9px 12px; }.diagnostic-map :deep(.proximity-layout) { display: block; }.diagnostic-map :deep(.proximity-filters) { border-right: 0; }.diagnostic-map :deep(.senegal-map) { min-height: 340px; }.diagnostic-map :deep(.nearby-list) { display: block; } }
.results-stack { display: grid; gap: 22px; animation: page-enter .55s cubic-bezier(.2,.75,.25,1) both; }.diagnostic-section { animation: none; }.recommendations { margin: 0; padding: 30px 34px 34px; border: 1px solid #dfece8; border-radius: 16px; background: linear-gradient(145deg, #f8fcfb 0%, #eef8f5 100%); box-shadow: 0 16px 38px rgba(21,70,74,.07); }.recommendation-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 8px; }.recommendation-heading h2 { margin: 7px 0 5px; color: #102b3b; font-size: clamp(23px, 2.4vw, 31px); letter-spacing: -.7px; }.recommendation-heading p { margin: 0; color: #70898a; font-size: 12px; }.location-primary { flex: 0 0 auto; padding: 12px 16px; border: 1px solid #b8d8d0; border-radius: 9px; background: #fff; color: #168273; font: inherit; font-size: 11px; font-weight: 800; cursor: pointer; box-shadow: 0 7px 17px rgba(22,130,115,.1); transition: transform .2s ease, box-shadow .2s ease; }.location-primary:hover { transform: translateY(-2px); box-shadow: 0 11px 22px rgba(22,130,115,.16); }.recommendations .location-help { margin: 12px 0 0; padding: 13px 15px; border-radius: 9px; background: rgba(255,255,255,.65); }.recommendations .diagnostic-map { display: block; margin-top: 20px; }.result-actions { display: grid; gap: 5px; padding: 0 12px; }.result-actions .main-action { max-width: 640px; margin: 0 auto; }.result-actions .restart-action { margin-top: 8px; }
.workspace { width: min(100% - 56px, 1180px); }.diagnostic-section, .result-actions { position: relative; }main { background: #102c49; background-image: radial-gradient(ellipse at 50% 0%, #214767 0, #102c49 48%, #0b2038 100%); }.progress-line { color: #afc2ce; }.progress-step.active { color: #54c8b5; }.progress-step.active b { color: #54c8b5; }.diagnostic-section { background: #fff; box-shadow: 0 24px 55px rgba(0,0,0,.22); }.results-stack { gap: 20px; }.recommendations { background: linear-gradient(145deg, #edf5f3 0%, #e0ebe9 100%); }
.workspace { width: min(100% - 48px, 1040px); }.form-card, .result-card { padding: 44px 40px 38px; border-radius: 18px; }.form-card { padding-top: 48px; }.card-heading { margin-bottom: 48px; }.card-heading h2 { font-size: 31px; line-height: 1.15; }.field-block { margin-bottom: 34px; }.field-block > label:first-child { margin-bottom: 14px; }.choice-grid { gap: 14px; }.choice { min-height: 102px; padding: 18px 10px; }.choice-icon { margin-bottom: 11px; }.field-block textarea, select { padding: 17px; }.field-hint { margin-top: 10px; }.details-row { gap: 30px; margin-top: 6px; }.location-only { grid-template-columns: 1fr; }.main-action { display: block; margin: 10px auto 0; padding: 18px 20px; max-width: 580px !important; }.privacy-note { margin-top: 18px; }.diagnostic-section { border-color: rgba(255,255,255,.75); box-shadow: 0 25px 65px rgba(0,0,0,.28); }.result-heading h2 { max-width: 590px; font-size: clamp(28px, 3vw, 38px); }.answer-grid { grid-template-columns: repeat(3, 1fr); gap: 11px; }.answer { min-height: 112px; border-radius: 14px; background: #f7fbfa; }.answer-main { background: #e5f6f0; border-color: #d5eee7; }.questions { background: #fffaf2; box-shadow: inset 3px 0 #e79b55; }.recommendations { padding: 28px 28px 30px; border-radius: 18px; box-shadow: 0 20px 50px rgba(0,0,0,.16); }.recommendation-heading h2 { font-size: clamp(22px, 2.4vw, 29px); }.diagnostic-map :deep(.proximity-layout) { grid-template-columns: 135px minmax(250px, 1fr) 215px; }.result-actions { padding: 0 8px; }
@media (max-width: 720px) { .recommendations { padding: 24px 18px 22px; }.recommendation-heading { display: block; }.location-primary { margin-top: 16px; }.result-actions { padding: 0; } }
</style>
