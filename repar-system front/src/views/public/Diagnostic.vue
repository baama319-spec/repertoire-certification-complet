<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import CarteProximite from '../../components/public/CarteProximite.vue'
import fondDiagnostic from '../../assets/images/image copy 9.png'
import {
  analyserDiagnostic,
  chargerReferentielsDiagnostic,
  chargerReparateursProches,
  trouverSpecialite,
  traduireDescription,
  transcrireAudio,
} from '../../services/serviceDiagnostic'

const formulaire = ref({ materiel: 'Smartphone', modele: '', description: '' })
const route = useRoute()
const analyseLancee = ref(false)
const analyseEnCours = ref(false)
const erreur = ref('')
const erreurVocale = ref('')
const enregistrementEnCours = ref(false)
const transcriptionEnCours = ref(false)
const traductionEnCours = ref(false)
const diagnostic = ref(null)
const localisations = ref([])
const specialites = ref([])
const referentielsEnCours = ref(true)
const reparateurs = ref([])
const position = ref(null)
const localisationActive = ref(false)
const localisationErreur = ref('')
const tempsEnregistrement = ref(0)
const photos = ref([])
const apercusPhotos = ref([])
const grilleAppareils = ref(null)
let enregistreurAudio = null
let fluxAudio = null
let minuterieEnregistrement = null
let chronometreEnregistrement = null
let dateDebutEnregistrement = null

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

const formatteurTemps = (secondes) => {
  const minutes = Math.floor(secondes / 60)
  const restantes = secondes % 60
  return `${String(minutes).padStart(2, '0')}:${String(restantes).padStart(2, '0')}`
}

const libererMicrophone = () => {
  if (minuterieEnregistrement) window.clearTimeout(minuterieEnregistrement)
  minuterieEnregistrement = null
  if (chronometreEnregistrement) window.clearInterval(chronometreEnregistrement)
  chronometreEnregistrement = null
  dateDebutEnregistrement = null
  tempsEnregistrement.value = 0
  fluxAudio?.getTracks().forEach((piste) => piste.stop())
  fluxAudio = null
}

const arreterEnregistrement = () => {
  if (minuterieEnregistrement) window.clearTimeout(minuterieEnregistrement)
  minuterieEnregistrement = null
  if (chronometreEnregistrement) window.clearInterval(chronometreEnregistrement)
  chronometreEnregistrement = null
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
    fluxAudio = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    })
    const formats = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus']
    const mimeType = formats.find((format) => window.MediaRecorder.isTypeSupported(format))
    enregistreurAudio = new window.MediaRecorder(fluxAudio, mimeType ? {
      mimeType,
      audioBitsPerSecond: 128000,
    } : {
      audioBitsPerSecond: 128000,
    })
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
      } catch (error) {
        erreurVocale.value = error.message
      } finally {
        transcriptionEnCours.value = false
      }
    }
    enregistreurAudio.start(250)
    enregistrementEnCours.value = true
    dateDebutEnregistrement = Date.now()
    chronometreEnregistrement = window.setInterval(() => {
      const duree = Math.min(Math.floor((Date.now() - dateDebutEnregistrement) / 1000), 120)
      tempsEnregistrement.value = duree
      if (duree >= 120) arreterEnregistrement()
    }, 250)
    minuterieEnregistrement = window.setTimeout(arreterEnregistrement, 120000)
  } catch (error) {
    libererMicrophone()
    erreurVocale.value = error.name === 'NotAllowedError'
      ? 'Autorisez l’accès au microphone pour enregistrer votre description.'
      : 'Impossible d’accéder au microphone. Vérifiez les autorisations ou saisissez le texte.'
  }
}

onBeforeUnmount(() => {
  apercusPhotos.value.forEach((apercu) => URL.revokeObjectURL(apercu.url))
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
}

const defilerAppareils = direction => {
  grilleAppareils.value?.scrollBy({
    left: direction * grilleAppareils.value.clientWidth * 0.8,
    behavior: 'smooth',
  })
}

const ajouterPhotos = (event) => {
  const fichiers = Array.from(event.target.files || [])
  if (!fichiers.length) return
  if (photos.value.length + fichiers.length > 3) {
    erreur.value = 'Vous pouvez joindre jusqu’à 3 photos maximum.'
    event.target.value = ''
    return
  }
  const typesAcceptes = ['image/jpeg', 'image/png', 'image/webp']
  const fichierInvalide = fichiers.find((fichier) => !typesAcceptes.includes(fichier.type) || fichier.size > 5 * 1024 * 1024)
  if (fichierInvalide) {
    erreur.value = !typesAcceptes.includes(fichierInvalide.type)
      ? 'Utilisez des photos JPG, PNG ou WEBP.'
      : 'Chaque photo doit faire 5 Mo maximum.'
    event.target.value = ''
    return
  }
  photos.value.push(...fichiers)
  apercusPhotos.value.push(...fichiers.map((fichier) => ({
    name: fichier.name,
    url: URL.createObjectURL(fichier),
  })))
  erreur.value = ''
  event.target.value = ''
}

const retirerPhoto = (index) => {
  const apercu = apercusPhotos.value[index]
  if (apercu?.url) URL.revokeObjectURL(apercu.url)
  photos.value.splice(index, 1)
  apercusPhotos.value.splice(index, 1)
}

const lancerAnalyse = async () => {
  erreur.value = ''
  if (traductionEnCours.value) return
  analyseEnCours.value = true
  try {
    validerDiagnostic()
    traductionEnCours.value = true
    const resultatTraduction = await traduireDescription(formulaire.value.description.trim())
    traductionEnCours.value = false
    diagnostic.value = await analyserDiagnostic({
      appareil: formulaire.value.materiel,
      marque: formulaire.value.modele,
      description: resultatTraduction.description_francaise,
    }, photos.value)
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

const recommencer = () => {
  analyseLancee.value = false
  diagnostic.value = null
  reparateurs.value = []
  position.value = null
  localisationActive.value = false
  erreur.value = ''
  erreurVocale.value = ''
}

onMounted(async () => {
  try {
    const referentiels = await chargerReferentielsDiagnostic()
    localisations.value = referentiels.localisations
    specialites.value = referentiels.specialites
  } catch (error) {
    erreur.value = error.message
  } finally {
    referentielsEnCours.value = false
  }
})
</script>

<template>
  <div class="home-page"><EntetePublic /></div>
  <main :style="{ '--diagnostic-background': `url(${fondDiagnostic})` }">
    <section class="workspace" aria-label="Formulaire de diagnostic">
      <div v-if="!analyseLancee" class="form-card">
        <div class="card-heading"><div><h2>Parlez-nous de votre appareil</h2></div></div>
        <p v-if="route.query.reparateur" class="field-hint">Votre demande sera transmise au réparateur dont vous consultez le profil.</p>
        <div class="field-block">
          <h2 class="device-title">L’appareil à réparer</h2>
          <div class="device-carousel">
            <button class="device-scroll" type="button" aria-label="Défiler les appareils vers la gauche" @click="defilerAppareils(-1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg></button>
            <div ref="grilleAppareils" class="device-grid" role="group" aria-label="Type d’appareil">
              <button v-for="type in ['Smartphone', 'Ordinateur', 'Tablette', 'Télévision']" :key="type" type="button" :class="['device-choice', { selected: formulaire.materiel === type }]" :aria-pressed="formulaire.materiel === type" @click="formulaire.materiel = type">
                <svg class="device-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <template v-if="type === 'Smartphone'"><rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/></template>
                  <template v-else-if="type === 'Ordinateur'"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M2 21h20l-2-4H4l-2 4Z"/></template>
                  <template v-else-if="type === 'Tablette'"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M11 18h2"/></template>
                  <template v-else><rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 22h8m-4-4v4"/></template>
                </svg>
                <span>{{ type }}</span>
              </button>
            </div>
            <button class="device-scroll" type="button" aria-label="Défiler les appareils vers la droite" @click="defilerAppareils(1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg></button>
          </div>
        </div>
        <div class="field-block"><label for="modele">Marque et modèle <small>(facultatif)</small></label><input id="modele" v-model.trim="formulaire.modele" maxlength="80" placeholder="Ex. Samsung Galaxy S21"></div>
        <div class="field-block">
          <label for="description">Que se passe-t-il ?</label>
          <div class="voice-input-wrap">
            <textarea id="description" v-model.trim="formulaire.description" placeholder="Ex. : mon téléphone est tombé, l’écran s’allume mais le tactile ne répond plus…" rows="5"></textarea>
            <button
              class="voice-action floating"
              :class="{ 'is-recording': enregistrementEnCours }"
              type="button"
              :disabled="transcriptionEnCours"
              :aria-pressed="enregistrementEnCours"
              @click="enregistrementEnCours ? arreterEnregistrement() : demarrerEnregistrement()"
              :title="enregistrementEnCours ? 'Arrêter l’enregistrement' : 'Décrire à voix haute'"
            >
              <span class="voice-button-content">
                <AppIcon :name="enregistrementEnCours ? 'mic-off' : 'mic'" :size="16" stroke-width="2.2" />
                <span v-if="enregistrementEnCours" class="recording-timer">{{ formatteurTemps(tempsEnregistrement) }}</span>
              </span>
            </button>
          </div>
          <p v-if="enregistrementEnCours" class="voice-status" aria-live="polite">Enregistrement en cours — {{ formatteurTemps(tempsEnregistrement) }} / 02:00.</p>
          <p v-else-if="transcriptionEnCours" class="voice-status" aria-live="polite">Transcription automatique de votre audio…</p>
          <p v-if="erreurVocale" class="error-message" role="alert">{{ erreurVocale }}</p>
        </div>
        <section class="field-block photo-upload-block">
          <h2 class="photo-upload-heading">Ajoutez des photos de votre problème</h2>
          <label v-if="!apercusPhotos.length" class="photo-upload-area" for="diagnostic-photos">
            <input id="diagnostic-photos" type="file" accept="image/jpeg,image/png,image/webp" multiple class="hidden-file-input" @change="ajouterPhotos">
            <span class="photo-upload-icon"><AppIcon name="image" :size="22" /></span>
            <span class="photo-upload-actions">
              <span class="photo-upload-browse"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V9m0 0 3 3m-3-3-3 3"/><path d="M20 16.6a4.4 4.4 0 0 0-1.5-8.54A6.5 6.5 0 0 0 6 9.5a3.5 3.5 0 0 0 .5 7.03"/></svg>Choisir des photos</span>
              <span class="photo-upload-formats">JPG, PNG ou WebP · 5 Mo maximum par image</span>
            </span>
          </label>
          <div v-else class="diagnostic-photo-gallery">
            <div v-for="(photo, index) in apercusPhotos" :key="`${photo.name}-${index}`" class="diagnostic-photo-card">
              <img :src="photo.url" :alt="photo.name">
              <button type="button" class="diagnostic-remove-photo" aria-label="Retirer la photo" @click="retirerPhoto(index)">×</button>
            </div>
            <label v-if="apercusPhotos.length < 3" class="diagnostic-add-photo" for="diagnostic-photos-more">
              <input id="diagnostic-photos-more" type="file" accept="image/jpeg,image/png,image/webp" class="hidden-file-input" @change="ajouterPhotos">
              <AppIcon name="plus" :size="20" />
              <span>Ajouter une autre<br>photo</span>
            </label>
          </div>
        </section>
        <p v-if="erreur" class="error-message" role="alert">{{ erreur }}</p>
        <p v-if="referentielsEnCours" class="field-hint">Chargement des zones d’intervention…</p>
        <button class="main-action" type="button" :disabled="analyseEnCours || traductionEnCours || enregistrementEnCours || transcriptionEnCours || formulaire.description.trim().length < 10" @click="lancerAnalyse">{{ analyseEnCours ? 'Analyse en cours…' : 'Lancer mon diagnostic IA' }} <AppIcon name="arrow-right" :size="18" /></button>
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
.home-page { height: 70px; }
.home-page :deep(.header) { position: fixed; top: 0; right: 0; left: 0; z-index: 1000; box-sizing: border-box; }
main { min-height: 70vh; padding: 20px 0 64px; background-image: linear-gradient(rgba(7, 23, 42, .48), rgba(7, 23, 42, .58)), var(--diagnostic-background); background-position: center; background-size: cover; background-attachment: fixed; color: #102b3b; }
.workspace { width: min(calc(100% - 40px), 1120px); margin: 0 auto; }
.form-card, .result-card, .recommendations { padding: clamp(24px, 5vw, 44px); border: 1px solid #e3ebe8; border-radius: 18px; background: #fff; box-shadow: 0 20px 50px rgba(0,0,0,.15); }
.form-card { padding: clamp(22px, 3vw, 36px); border-color: rgba(255,255,255,.2); background: rgba(5,12,24,.58); box-shadow: 0 20px 50px rgba(0,0,0,.2); backdrop-filter: blur(3px); }
.form-card .card-heading h2, .form-card .field-block > label, .form-card .device-title, .form-card .photo-upload-heading { color: #fff; }
.form-card .field-block small { color: rgba(255,255,255,.72); }
.card-heading h2, .result-card h2, .recommendation-heading h2 { margin: 0 0 8px; color: #102b3b; font-size: clamp(23px, 3vw, 31px); }
.card-heading p, .field-hint, .privacy-note, .location-help { color: #718788; font-size: 12px; line-height: 1.55; }
.field-block { margin: 34px 0; }
.field-block > label, .description-label-row > label { display: block; margin-bottom: 11px; color: #284750; font-size: 13px; font-weight: 800; }
.field-block small { color: #819596; font-weight: 400; }
.device-title { margin: 0 0 18px; color: #1e2a2d; font-size: 13px; letter-spacing: 0; line-height: 1.2; }
.device-carousel { display: grid; grid-template-columns: 34px minmax(0, 1fr) 34px; align-items: center; gap: 12px; width: 100%; }
.device-grid { display: flex; min-width: 0; gap: 14px; overflow-x: auto; scrollbar-width: none; scroll-snap-type: x mandatory; scroll-behavior: smooth; width: 100%; }
.device-grid::-webkit-scrollbar { display: none; }
.device-choice { display: flex; flex: 1 1 0; min-width: 0; min-height: 96px; box-sizing: border-box; flex-direction: column; align-items: center; justify-content: center; gap: 6px; padding: 12px 10px; border: 1px solid #dfe9e7; border-radius: 12px; background: #fbfdfc; color: #526f70; font: inherit; font-size: 15px; font-weight: 500; cursor: pointer; scroll-snap-align: start; transition: all .2s ease; }
.device-choice.selected, .device-choice:hover { border-color: #168273; background: #edf9f4; color: #087f70; box-shadow: 0 8px 18px rgba(22, 130, 115, .12); }
.device-icon { width: 26px; height: 26px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.device-scroll { display: grid; width: 34px; height: 34px; place-items: center; border: 1px solid #b8d8d0; border-radius: 50%; background: #fff; color: #168273; cursor: pointer; transition: all .18s ease; }
.device-scroll:hover { transform: scale(1.06); background: #168273; color: #fff; }
.device-scroll svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.field-block input, .field-block textarea, .field-block select { width: 100%; box-sizing: border-box; border: 1px solid #dbe7e4; border-radius: 10px; padding: 14px; background: #fbfdfc; color: #284750; font: inherit; font-size: 14px; }
.field-block textarea { resize: vertical; }
.field-block input:focus, .field-block textarea:focus, .field-block select:focus { outline: 2px solid #168273; outline-offset: 1px; }
.photo-upload-heading { margin: 0 0 11px; color: #284750; font-size: 13px; font-weight: 800; line-height: normal; }
.field-block > label.photo-upload-area { display: grid; width: 100%; min-height: 202px; box-sizing: border-box; grid-template-columns: minmax(0, 1fr); justify-items: center; align-content: center; gap: 8px; padding: 16px; border: 1px dashed #90d7c9; border-radius: 10px; background: linear-gradient(180deg, #f7fcfa 0%, #f1faf7 100%); color: #284750; text-align: center; cursor: pointer; transition: border-color .2s ease, background .2s ease, box-shadow .2s ease; }
.photo-upload-area:hover { border-color: #168273; background: #f0faf6; box-shadow: 0 8px 20px rgba(22, 130, 115, .08); }
.photo-upload-area:focus-within { outline: 2px solid #168273; outline-offset: 3px; }
.hidden-file-input { display: none; }
.photo-upload-icon { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 50%; background: #e1f3ee; color: #078575; }
.photo-upload-actions { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.photo-upload-browse { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 9px 18px; border: 1px solid #078575; border-radius: 8px; background: #078575; color: #fff; font-size: 12px; font-weight: 800; transition: background .2s ease, transform .2s ease; }
.photo-upload-browse svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.photo-upload-formats { display: block; color: #718788; font-size: 10px; line-height: 1.4; text-align: center; }
.photo-upload-area:hover .photo-upload-browse { transform: translateY(-1px); background: #116d61; }
.diagnostic-photo-gallery { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; min-height: 112px; padding: 12px 16px; border: 1px dashed #90d7c9; border-radius: 10px; background: linear-gradient(180deg, #f7fcfa 0%, #f1faf7 100%); }
.diagnostic-photo-card { position: relative; flex: 0 0 102px; width: 102px; height: 90px; overflow: hidden; border: 1px solid #dbe7e4; border-radius: 8px; background: #f7faf9; }
.diagnostic-photo-card img { display: block; width: 100%; height: 100%; object-fit: cover; }
.diagnostic-remove-photo { position: absolute; top: 4px; right: 4px; display: grid; width: 21px; height: 21px; place-items: center; padding: 0; border: 1px solid rgba(255,255,255,.85); border-radius: 50%; background: rgba(16, 43, 59, .78); color: #fff; font: inherit; font-size: 15px; line-height: 1; cursor: pointer; }
.diagnostic-add-photo { display: flex; flex: 0 0 122px; width: 122px; height: 90px; box-sizing: border-box; flex-direction: column; align-items: center; justify-content: center; gap: 7px; border: 1px dashed #80d3c2; border-radius: 9px; background: rgba(255,255,255,.55); color: #078575; font-size: 11px; font-weight: 700; line-height: 1.35; text-align: center; cursor: pointer; transition: background .18s ease, border-color .18s ease; }
.diagnostic-add-photo:hover { border-color: #078575; background: #eaf8f3; }
.description-label-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.voice-action, .location-primary, .restart-action { padding: 11px 14px; border: 1px solid #b8d8d0; border-radius: 9px; background: #f2faf7; color: #087f70; font: inherit; font-size: 12px; font-weight: 800; cursor: pointer; }
.voice-input-wrap { position: relative; }
.voice-input-wrap textarea { padding-right: 64px; }
.voice-action { position: absolute; right: 12px; bottom: 12px; display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; min-width: 42px; padding: 0; border-radius: 50%; border: 1px solid #a9d9d1; background: linear-gradient(180deg, #f4fbf9 0%, #ebf8f4 100%); box-shadow: 0 8px 18px rgba(22, 130, 115, .12); transition: all .2s ease; }
.voice-action[aria-pressed="true"] { width: auto; min-width: 80px; padding: 0 10px; border-radius: 999px; border-color: #d65b5b; background: linear-gradient(180deg, #fff3f3 0%, #ffeaea 100%); }
.voice-action:hover { transform: translateY(-1px); }
.voice-action:disabled { opacity: .65; cursor: wait; }
.voice-button-content { display: inline-flex; align-items: center; justify-content: center; gap: 8px; white-space: nowrap; }
.recording-timer { display: inline-flex; align-items: center; justify-content: center; min-width: 42px; height: 22px; padding: 2px 6px; border-radius: 999px; background: rgba(22,130,115,.08); color: #0d5d52; font-size: 10px; font-weight: 800; }
.voice-action[aria-pressed="true"] .recording-timer { background: rgba(211,54,70,.1); color: #a82b39; }
.voice-status { color: #168273; font-size: 12px; }
.voice-action[aria-pressed="true"] .app-icon { color: #d33646; }
.voice-action:not([aria-pressed="true"]) .app-icon { color: #168273; }
.main-action { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; margin-top: 18px; padding: 16px; border: 0; border-radius: 10px; background: #168273; color: white; font: inherit; font-weight: 800; cursor: pointer; }
.main-action:disabled { opacity: .5; cursor: not-allowed; }
.privacy-note { margin: 14px 0 0; text-align: center; }
.error-message { padding: 12px 14px; border-radius: 8px; background: #fff0f0; color: #a8323b; font-size: 12px; }
.results-stack { display: grid; gap: 18px; }
.result-topline { margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #edf2f0; color: #1e2a2d; font-size: 12px; font-weight: 800; }
.answer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 24px 0; }
.answer { padding: 17px; border: 1px solid #edf2f0; border-radius: 12px; background: #fff; }
.answer-main { background: #fff; }
.answer span { display: block; margin-bottom: 10px; color: #1f2b2d; font-size: 11px; font-weight: 800; }
.answer strong { color: #1d2c2f; font-size: 14px; line-height: 1.5; }
.answer p, .answer li, .questions li, .disclaimer { color: #465d5f; font-size: 12px; line-height: 1.6; }
.answer ul, .questions ul { padding-left: 18px; }
.result-specialty { color: #4a5d60; font-size: 13px; }
.questions { margin: 18px 0; padding: 16px; border: 1px solid #edf2f0; border-left: 3px solid #dfe7e5; background: #fff; }
.recommendation-heading { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.recommendation-heading h2 { font-size: 22px; }
.location-help { margin-bottom: 0; }
.diagnostic-map :deep(.proximity-section) { width: 100%; padding: 0; background: transparent; }
.diagnostic-map :deep(.proximity-layout) { width: 100%; margin: 0; }
.restart-action { display: block; margin: 0 auto; background: #fff; }
@media (max-width: 800px) { .home-page { height: 62px; } }
@media (max-width: 650px) { .workspace { width: min(calc(100% - 20px), 1200px); }.form-card { padding: 20px 16px; }.device-grid { gap: 10px; }.device-choice { min-height: 96px; font-size: 14px; }.answer-grid { grid-template-columns: repeat(2, 1fr); }.recommendation-heading { align-items: flex-start; flex-direction: column; }.voice-action { white-space: nowrap; } }
@media (max-width: 420px) { .device-choice { min-width: 190px; }.answer-grid { grid-template-columns: 1fr; }.description-label-row { align-items: flex-start; flex-direction: column; }.voice-action { width: 100%; } }
</style>
