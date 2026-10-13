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
const formulaire = ref({ description: '', annee_experience: '', specialites: [], zones_intervention: [], latitude: null, longitude: null, photo_carte_identite: null, documents: [] })
const connecte = computed(() => !!utilisateur.value)
const statut = computed(() => profil.value?.statut_verification)
const localisationEnCours = ref(false)
const libelleZone = (zone) => [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ')
const detecterTypeDocument = (nom = '') => {
  const texte = nom.toLowerCase()
  if (texte.includes('dipl')) return 'DIPLOME'
  if (texte.includes('certif')) return 'CERTIFICAT'
  return 'AUTRE'
}

onMounted(async () => {
  if (!connecte.value || utilisateur.value.role === 'ADMINISTRATEUR') return
  chargement.value = true
  try {
    const [candidature, donneesSpecialites, donneesZones] = await Promise.all([chargerCandidature(), api('/specialites/'), api('/localisations/')])
    profil.value = candidature
    if (candidature) {
      enregistrerUtilisateur({
        ...utilisateur.value,
        profil_reparateur: {
          id: candidature.id,
          statut_verification: candidature.statut_verification,
          profil_verifie: candidature.profil_verifie,
        },
      })
    }
    specialites.value = donneesSpecialites.results || donneesSpecialites
    zones.value = donneesZones.results || donneesZones
    if (candidature) formulaire.value = { description: candidature.description || '', annee_experience: candidature.annee_experience || '', specialites: candidature.specialites || [], zones_intervention: candidature.zones_intervention || [], latitude: candidature.latitude, longitude: candidature.longitude }
  } catch (err) { erreur.value = err.message } finally { chargement.value = false }
})

function validerCandidature () {
  const description = formulaire.value.description.trim()
  if (!description || description.length < 20) {
    throw new Error('La présentation professionnelle doit contenir au moins 20 caractères.')
  }
  if (!formulaire.value.annee_experience || Number(formulaire.value.annee_experience) < 0 || Number(formulaire.value.annee_experience) > 99) {
    throw new Error('Veuillez indiquer un nombre d’années d’expérience valide.')
  }
  if (!Array.isArray(formulaire.value.specialites) || formulaire.value.specialites.length === 0) {
    throw new Error('Sélectionnez au moins une spécialité.')
  }
  if (!Array.isArray(formulaire.value.zones_intervention) || formulaire.value.zones_intervention.length === 0) {
    throw new Error('Sélectionnez au moins une zone d’intervention.')
  }
  if (!formulaire.value.photo_carte_identite) {
    throw new Error('Ajoutez une photo de votre carte d’identité pour finaliser votre candidature.')
  }
  if (formulaire.value.latitude == null || formulaire.value.longitude == null) {
    throw new Error('Activez votre localisation pour enregistrer votre candidature.')
  }
}

function gererCarteIdentite (event) {
  const fichier = event.target.files?.[0]
  if (fichier) formulaire.value.photo_carte_identite = fichier
}

function ajouterDocument () {
  formulaire.value.documents.push({ file: null, type: 'AUTRE' })
}

function retirerDocument (index) {
  formulaire.value.documents = formulaire.value.documents.filter((_, i) => i !== index)
}

function gererDocument (index, event) {
  const fichier = event.target.files?.[0]
  if (!fichier) return
  formulaire.value.documents[index] = {
    file: fichier,
    type: detecterTypeDocument(fichier.name),
  }
}

function changerTypeDocument (index, type) {
  formulaire.value.documents[index].type = type
}

async function soumettre () {
  erreur.value = ''
  try {
    validerCandidature()
    envoi.value = true
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
      <div class="etapes" aria-label="Les étapes pour devenir réparateur"><article><div class="etape-top"><b>01</b></div><h2>Créez votre compte</h2><p>Utilisez un seul compte pour tous vos espaces.</p></article><span class="etape-arrow" aria-hidden="true">›</span><article><div class="etape-top"><b>02</b></div><h2>Complétez votre profil</h2><p>Ajoutez vos compétences et zones d’intervention.</p></article><span class="etape-arrow" aria-hidden="true">›</span><article><div class="etape-top"><b>03</b></div><h2>Faites vérifier votre profil</h2><p>Nous vérifions votre candidature avant validation.</p></article></div>
      <div class="actions"><RouterLink class="secondary" :to="{ path: '/connexion', query: { redirection: '/devenir-reparateur' } }">Se connecter</RouterLink><RouterLink class="primary" :to="{ path: '/inscription', query: { redirection: '/devenir-reparateur' } }">Créer mon compte</RouterLink></div>
    </section>

    <section v-else-if="utilisateur.role === 'ADMINISTRATEUR'" class="message"><h1>Espace administrateur</h1><p>Les candidatures réparateur se gèrent depuis votre espace d’administration.</p><RouterLink class="primary" to="/admin">Accéder à l’administration</RouterLink></section>
    <p v-else-if="chargement" class="message">Chargement de votre candidature…</p>
    <section v-else-if="succes || statut === 'EN_ATTENTE'" class="message"><span class="status wait">En attente de vérification</span><h1>Candidature envoyée</h1><p>Votre candidature a bien été enregistrée. Vous ne serez visible ni accessible comme réparateur qu’après validation par un administrateur.</p><div class="actions"><RouterLink class="secondary" to="/">Retour à l’accueil</RouterLink></div></section>
    <section v-else-if="statut === 'VALIDEE'" class="message"><span class="status verified">Candidature validée</span><h1>Votre candidature est validée</h1><p>Vous pouvez maintenant accéder à votre espace réparateur et apparaître dans l’annuaire. La certification Pro reste une décision distincte.</p><div class="actions"><RouterLink class="secondary" to="/">Retour à l’accueil</RouterLink><RouterLink class="primary" to="/pro/demandes">Accéder à mon espace réparateur</RouterLink></div></section>
    <section v-else-if="profil?.profil_verifie" class="message"><span class="status verified">Certifié Pro</span><h1>Vous êtes déjà réparateur certifié</h1><p>Votre profil professionnel est certifié.</p><RouterLink class="primary" to="/pro/demandes">Accéder à mon espace réparateur</RouterLink></section>

    <form v-else class="candidature" @submit.prevent="soumettre">
      <header><span class="eyebrow">DEVENIR RÉPARATEUR</span><h1>{{ statut === 'REFUSEE' ? 'Modifiez votre candidature' : 'Votre profil professionnel' }}</h1><p>Vos informations personnelles sont reprises depuis votre compte. Complétez uniquement vos données professionnelles.</p></header>
      <p v-if="statut === 'REFUSEE' && profil.motif_refus" class="refus">{{ profil.motif_refus }}</p><p v-if="erreur" class="error">{{ erreur }}</p>
      <section class="form-section"><h2>Profil professionnel</h2><label>Années d’expérience<input v-model.number="formulaire.annee_experience" type="number" min="0" max="99" required></label><label>Présentation professionnelle<textarea v-model.trim="formulaire.description" maxlength="1000" required placeholder="Décrivez votre expérience et les réparations que vous réalisez."></textarea></label></section>
      <section class="form-section"><h2>Vos spécialités</h2><p v-if="!specialites.length">Aucune spécialité disponible.</p><div class="choices"><label v-for="item in specialites" :key="item.id"><input v-model="formulaire.specialites" type="checkbox" :value="item.id"><span>{{ item.nom }}</span></label></div></section>
      <section class="form-section"><h2>Zones d’intervention</h2><p v-if="!zones.length">Aucune zone disponible.</p><div class="choices"><label v-for="zone in zones" :key="zone.id"><input v-model="formulaire.zones_intervention" type="checkbox" :value="zone.id"><span>{{ libelleZone(zone) }}</span></label></div></section>
      <section class="form-section documents-section"><h2>Pièces justificatives</h2>
        <div class="upload-row">
          <label class="upload-box required">
            <span class="upload-label">Carte d’identité obligatoire</span>
            <span class="upload-button">Parcourir…</span>
            <input type="file" accept="image/*,.pdf" @change="gererCarteIdentite" required>
          </label>
          <span class="file-name">{{ formulaire.photo_carte_identite ? formulaire.photo_carte_identite.name : 'Aucun fichier sélectionné.' }}</span>
        </div>

        <div class="documents-list">
          <div v-for="(document, index) in formulaire.documents" :key="`doc-${index}`" class="document-item">
            <label class="upload-box">
              <span class="upload-label">Pièce justificative {{ index + 1 }}</span>
              <span class="upload-button">Ajouter…</span>
              <input type="file" accept=".pdf,image/*" @change="gererDocument(index, $event)">
            </label>
            <select v-model="document.type" @change="changerTypeDocument(index, document.type)">
              <option value="DIPLOME">Diplôme</option>
              <option value="CERTIFICAT">Certificat</option>
              <option value="AUTRE">Autre</option>
            </select>
            <button type="button" class="remove-button" @click="retirerDocument(index)" v-if="formulaire.documents.length > 1">Retirer</button>
            <span class="document-file-name">{{ document.file ? document.file.name : 'Aucun fichier sélectionné.' }}</span>
          </div>
          <button type="button" class="secondary add-doc" @click="ajouterDocument">+ Ajouter une autre pièce</button>
        </div>
      </section>
      <section class="form-section localisation-section"><h2>Ma localisation</h2><p>Autorisez ReparSystem à utiliser votre position pour afficher votre profil aux clients proches.</p><button type="button" class="secondary location-button" :disabled="localisationEnCours" @click="activerLocalisation">{{ localisationEnCours ? 'Récupération en cours…' : formulaire.latitude != null ? 'Actualiser ma position' : 'Autoriser ma position' }}</button><small v-if="formulaire.latitude != null" class="coordinates">Position enregistrée : {{ Number(formulaire.latitude).toFixed(4) }}, {{ Number(formulaire.longitude).toFixed(4) }}</small></section>
      <section class="recap"><h2>Vérifiez vos informations</h2><p><b>{{ utilisateur.prenom }} {{ utilisateur.nom }}</b> · {{ utilisateur.email }} · {{ utilisateur.telephone || 'Téléphone non renseigné' }}</p><p>Carte d’identité obligatoire + documents complémentaires.</p></section>
      <button class="primary submit" :disabled="envoi">{{ envoi ? 'Envoi en cours…' : statut === 'REFUSEE' ? 'Renvoyer ma candidature' : 'Envoyer ma candidature' }}</button>
    </form>
  </main>
  <PiedDePage />
</template>

<style scoped>
.devenir {
  background: #f6f8fc;
  min-height: 620px;
  padding: 68px max(5.5%, 48px);
}

.intro,
.candidature,
.message {
  max-width: 920px;
  margin: auto;
}

.intro {
  text-align: center;
}

.intro h1,
.candidature h1,
.message h1 {
  font-size: 34px;
  margin: 14px 0;
  color: #0b152b;
}

.intro > p,
.candidature header p,
.message p {
  color: #68778b;
  line-height: 1.6;
  font-size: 14px;
}

.etapes {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  margin: 42px 0;
  padding: 22px 18px;
  background: #fff;
  border: 1px solid #e3e9f1;
  border-radius: 18px;
  box-shadow: 0 18px 45px rgba(20, 49, 76, 0.08);
}

.etapes article,
.form-section,
.recap,
.message {
  background: #fff;
  border: 1px solid #e3e9f1;
  border-radius: 13px;
  padding: 25px;
  text-align: left;
}

.etapes article {
  min-height: 220px;
  padding: 22px 20px;
}

.etape-top {
  display: flex;
  align-items: center;
  gap: 16px;
}

.etapes b {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #087f70;
  color: #fff;
  font-size: 12px;
}

.etapes h2,
.form-section h2,
.recap h2 {
  font-size: 19px;
  margin: 20px 0 10px;
}

.etapes p {
  margin: 0;
  color: #718094;
  font-size: 13px;
  line-height: 1.6;
}

.etape-arrow {
  display: flex;
  justify-content: center;
  align-items: center;
  color: #087f70;
  font-size: 40px;
  font-weight: 300;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.primary,
.secondary {
  display: inline-block;
  border-radius: 8px;
  padding: 13px 19px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
}

.primary {
  background: #087f70;
  color: #fff;
}

.secondary {
  background: #fff;
  border: 1px solid #dce4ee;
  color: #087f70;
}

.message {
  text-align: center;
  max-width: 600px;
  margin-top: 50px;
}

.message .actions {
  margin-top: 22px;
}

.status {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 11px;
}

.wait {
  background: #fff4d7;
  color: #9b6700;
}

.verified {
  background: #e5f8ee;
  color: #138451;
}

.candidature {
  background: #fff;
  border: 1px solid #e3e9f1;
  border-radius: 14px;
  padding: 32px;
}

.form-section {
  margin-top: 18px;
}

.form-section label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  margin-top: 14px;
}

.form-section input[type='number'],
.form-section textarea,
.form-section select {
  display: block;
  width: 100%;
  margin-top: 7px;
  border: 1px solid #d6e0ec;
  border-radius: 7px;
  padding: 11px;
  font: inherit;
  outline-color: #087f70;
  box-sizing: border-box;
}

.form-section input[type='number'] {
  height: 42px;
}

.form-section textarea {
  min-height: 115px;
  resize: vertical;
}

.choices {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.choices label {
  margin: 0;
  font-weight: 500;
  position: relative;
}

.choices input {
  position: absolute;
  opacity: 0;
}

.choices span {
  display: block;
  border: 1px solid #d6e0ec;
  border-radius: 7px;
  padding: 9px 12px;
  color: #526277;
  font-size: 12px;
}

.documents-section {
  display: grid;
  gap: 18px;
}

.upload-row,
.document-item {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) minmax(150px, 1fr);
  align-items: center;
  gap: 12px;
}

.upload-box {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  border: 1px solid #d9e7f7;
  border-radius: 10px;
  background: #f6fbff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-box:hover {
  border-color: #7db4ff;
  background: #edf7ff;
}

.upload-box input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-label {
  font-size: 13px;
  font-weight: 700;
  color: #174b50;
}

.upload-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 7px;
  background: #edf5ff;
  color: #0d6b7d;
  font-size: 12px;
  font-weight: 700;
}

.required .upload-button {
  background: #e8f7f1;
  color: #0f7a66;
}

.file-name,
.document-file-name {
  font-size: 12px;
  color: #4c6989;
  overflow-wrap: anywhere;
}

.document-item {
  grid-template-columns: minmax(220px, 1fr) 160px 110px 1fr;
}

.document-item select {
  height: 44px;
  border: 1px solid #d9e7f7;
  border-radius: 8px;
  padding: 0 12px;
  background: #fff;
  color: #174b50;
}

.remove-button {
  height: 44px;
  border: 1px solid #ffdddf;
  background: #fff4f5;
  color: #c9353d;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.add-doc {
  margin-top: 8px;
}

.localisation-section {
  display: grid;
  gap: 10px;
}

.localisation-section h2 {
  margin-bottom: 0;
}

.localisation-section p {
  margin: 0;
  color: #68778b;
  font-size: 12px;
  line-height: 1.5;
}

.location-button {
  margin-top: 14px;
  cursor: pointer;
}

.location-button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.coordinates {
  display: block;
  margin-top: 10px;
  color: #087f70;
  font-size: 11px;
  font-weight: 700;
}

.devenir-page :deep(.header) {
  background-image: linear-gradient(90deg, rgba(4, 27, 64, 0.7), rgba(4, 27, 64, 0.35)), var(--devenir-bg);
  background-position: center top;
  background-size: cover;
  color: #fff;
  border-bottom-color: rgba(255, 255, 255, 0.18);
}

.devenir-page :deep(.header a) {
  color: #fff;
}

.devenir-page :deep(.header .logo-reparsystem) {
  background: #fff;
  border-radius: 8px;
  padding: 3px;
}

.devenir-page :deep(.header .signup) {
  background: #087f70;
  color: #fff;
}

.devenir {
  background-image: var(--devenir-bg);
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
}

@media (max-width: 700px) {
  .etapes {
    grid-template-columns: 1fr;
    width: 100%;
    margin: 32px 0;
    padding: 30px 20px;
    gap: 12px;
  }

  .etapes article {
    min-height: 0;
    padding: 18px 16px;
  }

  .etape-arrow {
    transform: rotate(90deg);
    font-size: 25px;
  }

  .upload-row,
  .document-item {
    grid-template-columns: 1fr;
  }

  .document-item {
    padding-top: 10px;
  }

  .add-doc {
    width: 100%;
  }
}
</style>
