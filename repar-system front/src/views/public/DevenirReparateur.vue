<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import { useAuthentification } from '../../services/serviceAuthentification'
import { chargerCandidature, envoyerCandidature } from '../../services/serviceCandidatureReparateur'
import { api } from '../../services/api'
import imageFond from '../../assets/images/reparateur-hero-reference.png'

const router = useRouter()
const { utilisateur, enregistrerUtilisateur } = useAuthentification()
const profil = ref(null), specialites = ref([]), zones = ref([])
const chargement = ref(false), envoi = ref(false), erreur = ref(''), succes = ref(false)
const formulaire = ref({ description: '', annee_experience: '', specialites: [], zones_intervention: [], latitude: null, longitude: null })
const connecte = computed(() => !!utilisateur.value)
const statut = computed(() => profil.value?.statut_verification)
const localisationEnCours = ref(false)
const libelleZone = (zone) => [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ')

onMounted(async () => {
  if (!connecte.value || utilisateur.value.role === 'ADMINISTRATEUR') return
  chargement.value = true
  try {
    const [candidature, donneesSpecialites, donneesZones] = await Promise.all([chargerCandidature(), api('/specialites/'), api('/localisations/')])
    profil.value = candidature
    specialites.value = donneesSpecialites.results || donneesSpecialites
    zones.value = donneesZones.results || donneesZones
    if (candidature) formulaire.value = { description: candidature.description || '', annee_experience: candidature.annee_experience || '', specialites: candidature.specialites || [], zones_intervention: candidature.zones_intervention || [], latitude: candidature.latitude, longitude: candidature.longitude }
  } catch (err) { erreur.value = err.message } finally { chargement.value = false }
})

async function soumettre () {
  erreur.value = ''
  if (!formulaire.value.description.trim() || !formulaire.value.annee_experience || !formulaire.value.specialites.length || !formulaire.value.zones_intervention.length || formulaire.value.latitude == null || formulaire.value.longitude == null) {
    erreur.value = 'Activez votre localisation et complétez la présentation, l’expérience, une spécialité et une zone.'; return
  }
  envoi.value = true
  try {
    profil.value = await envoyerCandidature({ ...formulaire.value, annee_experience: Number(formulaire.value.annee_experience) })
    enregistrerUtilisateur({ ...utilisateur.value, profil_reparateur: { id: profil.value.id, statut_verification: profil.value.statut_verification, profil_verifie: profil.value.profil_verifie } })
    succes.value = true
  } catch (err) { erreur.value = err.message } finally { envoi.value = false }
}

function activerLocalisation () {
  if (!navigator.geolocation) { erreur.value = 'La géolocalisation n’est pas disponible sur ce navigateur.'; return }
  localisationEnCours.value = true
  erreur.value = ''
  navigator.geolocation.getCurrentPosition(({ coords }) => {
    formulaire.value.latitude = coords.latitude
    formulaire.value.longitude = coords.longitude
    localisationEnCours.value = false
  }, () => {
    localisationEnCours.value = false
    erreur.value = 'Autorisez la localisation pour enregistrer votre candidature.'
  }, { enableHighAccuracy: true, timeout: 10000 })
}
</script>

<template>
  <div class="devenir-page" :style="{ '--devenir-bg': `url(${imageFond})` }">
    <EntetePublic />
  </div>
  <main class="devenir" :style="{ '--devenir-bg': `url(${imageFond})` }">
    <section v-if="!connecte" class="intro">
      <div class="etapes" aria-label="Les étapes pour devenir réparateur"><h1>Partagez votre expertise avec ReparSystem</h1><article><div class="etape-top"><b>01</b></div><h2>Créez votre compte</h2><p>Utilisez un seul compte pour tous vos espaces.</p></article><span class="etape-arrow" aria-hidden="true">›</span><article><div class="etape-top"><b>02</b></div><h2>Complétez votre profil</h2><p>Ajoutez vos compétences et zones d’intervention.</p></article><span class="etape-arrow" aria-hidden="true">›</span><article><div class="etape-top"><b>03</b></div><h2>Faites vérifier votre profil</h2><p>Nous vérifions votre candidature avant validation.</p></article></div>
      <div class="actions"><RouterLink class="secondary" :to="{ path: '/connexion', query: { redirection: '/devenir-reparateur' } }">Se connecter</RouterLink><RouterLink class="primary" :to="{ path: '/inscription', query: { redirection: '/devenir-reparateur' } }">Créer mon compte</RouterLink></div>
    </section>

    <section v-else-if="utilisateur.role === 'ADMINISTRATEUR'" class="message"><h1>Espace administrateur</h1><p>Les candidatures réparateur se gèrent depuis votre espace d’administration.</p><RouterLink class="primary" to="/admin">Accéder à l’administration</RouterLink></section>
    <p v-else-if="chargement" class="message">Chargement de votre candidature…</p>
    <section v-else-if="succes || statut === 'EN_ATTENTE'" class="message"><span class="status wait">En attente de vérification</span><h1>Candidature envoyée</h1><p>Votre candidature a bien été enregistrée. Notre équipe va examiner votre profil.</p><div class="actions"><RouterLink class="secondary" to="/">Retour à l’accueil</RouterLink><RouterLink class="primary" to="/pro/profil">Voir mon profil</RouterLink></div></section>
    <section v-else-if="statut === 'VALIDEE'" class="message"><span class="status verified">Candidature validée</span><h1>Votre candidature est validée</h1><p>Votre profil est accepté. La certification Pro reste une décision distincte de l’administrateur.</p><RouterLink class="secondary" to="/">Retour à l’accueil</RouterLink></section>
    <section v-else-if="profil?.profil_verifie" class="message"><span class="status verified">Certifié Pro</span><h1>Vous êtes déjà réparateur certifié</h1><p>Votre profil professionnel est certifié.</p><RouterLink class="primary" to="/pro/demandes">Accéder à mon espace réparateur</RouterLink></section>

    <form v-else class="candidature" @submit.prevent="soumettre">
      <header><span class="eyebrow">DEVENIR RÉPARATEUR</span><h1>{{ statut === 'REFUSEE' ? 'Modifiez votre candidature' : 'Votre profil professionnel' }}</h1><p>Vos informations personnelles sont reprises depuis votre compte. Complétez uniquement vos données professionnelles.</p></header>
      <p v-if="statut === 'REFUSEE' && profil.motif_refus" class="refus">{{ profil.motif_refus }}</p><p v-if="erreur" class="error">{{ erreur }}</p>
      <section class="form-section"><h2>Profil professionnel</h2><label>Années d’expérience<input v-model.number="formulaire.annee_experience" type="number" min="0" max="99" required></label><label>Présentation professionnelle<textarea v-model.trim="formulaire.description" maxlength="1000" required placeholder="Décrivez votre expérience et les réparations que vous réalisez."></textarea></label></section>
      <section class="form-section"><h2>Vos spécialités</h2><p v-if="!specialites.length">Aucune spécialité disponible.</p><div class="choices"><label v-for="item in specialites" :key="item.id"><input v-model="formulaire.specialites" type="checkbox" :value="item.id"><span>{{ item.nom }}</span></label></div></section>
      <section class="form-section"><h2>Zones d’intervention</h2><p v-if="!zones.length">Aucune zone disponible.</p><div class="choices"><label v-for="zone in zones" :key="zone.id"><input v-model="formulaire.zones_intervention" type="checkbox" :value="zone.id"><span>{{ libelleZone(zone) }}</span></label></div></section>
      <section class="form-section localisation-section"><h2>📍 Ma localisation</h2><p>Autorisez ReparSystem à utiliser votre position pour afficher votre profil aux clients proches.</p><button type="button" class="secondary location-button" :disabled="localisationEnCours" @click="activerLocalisation">{{ localisationEnCours ? 'Récupération en cours…' : formulaire.latitude != null ? 'Actualiser ma position' : 'Autoriser ma position' }}</button><small v-if="formulaire.latitude != null" class="coordinates">Position enregistrée : {{ Number(formulaire.latitude).toFixed(4) }}, {{ Number(formulaire.longitude).toFixed(4) }}</small></section>
      <section class="recap"><h2>Vérifiez vos informations</h2><p><b>{{ utilisateur.prenom }} {{ utilisateur.nom }}</b> · {{ utilisateur.email }} · {{ utilisateur.telephone || 'Téléphone non renseigné' }}</p><p>Documents : aucun document n’est prévu par le backend actuel.</p></section>
      <button class="primary submit" :disabled="envoi">{{ envoi ? 'Envoi en cours…' : statut === 'REFUSEE' ? 'Renvoyer ma candidature' : 'Envoyer ma candidature' }}</button>
    </form>
  </main>
  <PiedDePage />
</template>

<style scoped>
.devenir{background:#f6f8fc;min-height:620px;padding:68px max(5.5%,48px)}.intro,.candidature,.message{max-width:920px;margin:auto}.intro{text-align:center}.intro h1,.candidature h1,.message h1{font-size:34px;margin:14px 0;color:#0b152b}.intro>p,.candidature header p,.message p{color:#68778b;line-height:1.6;font-size:14px}.etapes{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:42px 0}.etapes article,.form-section,.recap,.message{background:#fff;border:1px solid #e3e9f1;border-radius:13px;padding:25px;text-align:left}.etapes b{color:#087f70;font-size:18px}.etapes h2,.form-section h2,.recap h2{font-size:16px;margin:13px 0 8px}.etapes p{color:#718094;font-size:12px;line-height:1.5}.actions{display:flex;justify-content:center;gap:12px;flex-wrap:wrap}.primary,.secondary{display:inline-block;border-radius:8px;padding:13px 19px;font-size:12px;font-weight:700}.primary{background:#087f70;color:#fff}.secondary{background:#fff;border:1px solid #dce4ee;color:#087f70}.message{text-align:center;max-width:600px;margin-top:50px}.message .actions{margin-top:22px}.status{display:inline-block;padding:6px 10px;border-radius:20px;font-weight:700;font-size:11px}.wait{background:#fff4d7;color:#9b6700}.verified{background:#e5f8ee;color:#138451}.candidature{background:#fff;border:1px solid #e3e9f1;border-radius:14px;padding:32px}.form-section{margin-top:18px}.form-section label{display:block;font-size:12px;font-weight:700;margin-top:14px}.form-section input[type='number'],textarea{display:block;width:100%;margin-top:7px;border:1px solid #d6e0ec;border-radius:7px;padding:11px;font:inherit;outline-color:#087f70}.form-section input[type='number']{height:42px}.form-section textarea{min-height:115px;resize:vertical}.choices{display:flex;flex-wrap:wrap;gap:10px;margin-top:15px}.choices label{margin:0;font-weight:500}.choices input{position:absolute;opacity:0}.choices span{display:block;border:1px solid #d6e0ec;border-radius:7px;padding:9px 12px;color:#526277;font-size:12px}.choices input:checked+span{border-color:#087f70;background:#eef5ff;color:#087f70;font-weight:700}.recap{margin-top:18px;background:#f8fbff}.recap p{font-size:12px;color:#68778b}.submit{width:100%;border:0;margin-top:20px}.submit:disabled{opacity:.65;cursor:wait}.error,.refus{margin:18px 0;padding:12px;border-radius:7px;font-size:12px}.error{background:#fff0f1;color:#bb2639}.refus{background:#fff4d7;color:#806000}@media(max-width:700px){.devenir{padding:38px 20px}.intro h1,.candidature h1,.message h1{font-size:27px}.etapes{grid-template-columns:1fr}.candidature{padding:20px}.actions{align-items:stretch}.actions a{flex:1;text-align:center}.message{margin-top:0}}
.devenir{background:#f6f8fc;min-height:620px;padding:68px max(5.5%,48px)}.intro,.candidature,.message{max-width:920px;margin:auto}.intro{text-align:center}.intro h1,.candidature h1,.message h1{font-size:34px;margin:14px 0;color:#0b152b}.intro>p,.candidature header p,.message p{color:#68778b;line-height:1.6;font-size:14px}.etapes{display:grid;grid-template-columns:1fr 48px 1fr 48px 1fr;align-items:center;gap:0;width:min(1240px, calc(100vw - 72px));margin:42px 0 42px 50%;padding:44px 48px;background:#fff;border:1px solid #e3e9f1;border-radius:18px;box-shadow:0 18px 45px rgba(20,49,76,.08);text-align:left;transform:translateX(-50%);box-sizing:border-box}.etapes article{min-width:0;min-height:178px;padding:26px 20px;border:1px solid #dce7ee;border-radius:16px;background:linear-gradient(145deg,#fff 0%,#fbfefd 100%);transition:transform .2s ease,box-shadow .2s ease}.etapes article:hover{transform:translateY(-3px);box-shadow:0 12px 24px rgba(20,80,80,.09)}.etape-top{display:flex;align-items:center;gap:16px}.etape-icon{display:grid;width:56px;height:56px;place-items:center;border-radius:15px;background:#eaf7f5;color:#087f70;font-size:25px}.etapes b{display:grid;width:36px;height:36px;place-items:center;border-radius:50%;background:#087f70;color:#fff;font-size:12px}.etape-arrow{color:#087f70;font-size:40px;font-weight:300;text-align:center}.etapes h2,.form-section h2,.recap h2{font-size:19px;margin:20px 0 10px}.etapes p{margin:0;color:#718094;font-size:13px;line-height:1.6}.actions{display:flex;justify-content:center;gap:12px;flex-wrap:wrap}.primary,.secondary{display:inline-block;border-radius:8px;padding:13px 19px;font-size:12px;font-weight:700}.primary{background:#087f70;color:#fff}.secondary{background:#fff;border:1px solid #dce4ee;color:#087f70}.message{text-align:center;max-width:600px;margin-top:50px}.message .actions{margin-top:22px}.status{display:inline-block;padding:6px 10px;border-radius:20px;font-weight:700;font-size:11px}.wait{background:#fff4d7;color:#9b6700}.verified{background:#e5f8ee;color:#138451}.candidature{background:#fff;border:1px solid #e3e9f1;border-radius:14px;padding:32px}.form-section{margin-top:18px}.form-section label{display:block;font-size:12px;font-weight:700;margin-top:14px}.form-section input[type='number'],textarea{display:block;width:100%;margin-top:7px;border:1px solid #d6e0ec;border-radius:7px;padding:11px;font:inherit;outline-color:#087f70}.form-section input[type='number']{height:42px}.form-section textarea{min-height:115px;resize:vertical}.choices{display:flex;flex-wrap:wrap;gap:10px;margin-top:15px}.choices label{margin:0;font-weight:500}.choices input{position:absolute;opacity:0}.choices span{display:block;border:1px solid #d6e0ec;border-radius:7px;padding:9px 12px;color:#526277;font-size:12px}.choices input:checked+span{border-color:#087f70;background:#e6f7f3;color:#087f70}.localisation-section p{margin:0;color:#68778b;font-size:12px;line-height:1.5}.location-button{margin-top:14px;cursor:pointer}.location-button:disabled{opacity:.6;cursor:wait}.coordinates{display:block;margin-top:10px;color:#087f70;font-size:11px;font-weight:700}
.localisation-section p{margin:0;color:#68778b;font-size:12px;line-height:1.5}.location-button{margin-top:14px;cursor:pointer}.location-button:disabled{opacity:.6;cursor:wait}.coordinates{display:block;margin-top:10px;color:#087f70;font-size:11px;font-weight:700}
.devenir-page :deep(.header){background-image:linear-gradient(90deg,rgba(4,27,64,.7),rgba(4,27,64,.35)),var(--devenir-bg);background-position:center top;background-size:cover;color:#fff;border-bottom-color:rgba(255,255,255,.18)}.devenir-page :deep(.header a){color:#fff}.devenir-page :deep(.header .brand-mark){color:#fff}.devenir-page :deep(.header .signup){background:#087f70;color:#fff}
.devenir{background-image:var(--devenir-bg);background-position:center;background-size:cover;background-repeat:no-repeat}.etapes{background:linear-gradient(135deg,#e9f7f4 0%,#f1f5fc 100%);padding-top:54px;padding-bottom:54px}.etapes>h1{grid-column:1/-1;margin:0 0 44px;color:#0b152b;font-size:34px;line-height:1.1;text-align:center}.etapes article{min-height:230px;padding:30px 22px}
@media(max-width:700px){.etapes{grid-template-columns:1fr;width:100%;margin:32px 0;padding:30px 20px;gap:12px;transform:none}.etapes>h1{margin-bottom:28px;font-size:27px}.etapes article{min-height:0;padding:0}.etape-arrow{transform:rotate(90deg);font-size:25px}.etapes h2{margin-top:10px}}
</style>
