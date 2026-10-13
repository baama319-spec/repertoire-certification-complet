<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import PiedDePage from '../../components/public/PiedDePage.vue'
import { api } from '../../services/api'
import { creerDemande } from '../../services/serviceDemandes'

const route = useRoute()
const router = useRouter()
const formulaire = ref({ appareil: 'Smartphone', modele: '', description: '', localisation: '', mode_intervention: 'DOMICILE', adresse_intervention: '' })
const localisations = ref([])
const reparateurs = ref([])
const reparateur = ref(null)
const reparateurSelectionne = ref(route.query.reparateur ? String(route.query.reparateur) : '')
const chargement = ref(true)
const envoi = ref(false)
const erreur = ref('')
const succes = ref(false)
const positionGps = ref(null)
const localisationEnCours = ref(false)
const localisationErreur = ref('')
const diagnosticPourDemande = ref(null)
const photos = ref([])
const photoPreviews = ref([])
const descriptionComplete = computed(() => [formulaire.value.appareil, formulaire.value.modele].filter(Boolean).join(' · '))
const adresseRequise = computed(() => formulaire.value.mode_intervention === 'DOMICILE')
const adresseValide = computed(() => formulaire.value.adresse_intervention.trim().length >= 5 || !!positionGps.value)
const peutEnvoyer = computed(() => formulaire.value.description.trim().length >= 10
  && !!formulaire.value.localisation
  && (!adresseRequise.value || adresseValide.value))

const demandeIssueDiagnostic = computed(() => !!diagnosticPourDemande.value)
const grilleAppareils = ref(null)
const typesAppareils = ['Smartphone', 'Ordinateur', 'Tablette', 'Télévision', 'Électroménager', 'Autre']

const defilerAppareils = direction => {
  grilleAppareils.value?.scrollBy({ left: direction * grilleAppareils.value.clientWidth * 0.8, behavior: 'smooth' })
}

function chargerDiagnosticPourDemande () {
  if (route.query.diagnostic !== '1') return
  try {
    const sauvegarde = JSON.parse(sessionStorage.getItem('reparsystem-diagnostic') || 'null')
    if (sauvegarde?.resultat && typeof sauvegarde.resultat === 'object') {
      diagnosticPourDemande.value = sauvegarde
    }
  } catch (_) {
    sessionStorage.removeItem('reparsystem-diagnostic')
  }
}

onMounted(async () => {
  chargerDiagnosticPourDemande()
  try {
    const [zones, profil, listeReparateurs] = await Promise.all([
      api('/localisations/'),
      route.query.reparateur ? api(`/reparateurs/${route.query.reparateur}/`) : Promise.resolve(null),
      route.query.reparateur ? Promise.resolve([]) : api('/reparateurs/'),
    ])
    localisations.value = (zones.results || zones).filter(zone => zone.actif)
    reparateur.value = profil
    reparateurs.value = listeReparateurs.results || listeReparateurs
    const zonesDuReparateur = new Set(profil?.zones_intervention || [])
    const zoneProposee = localisations.value.find(zone => zonesDuReparateur.has(zone.id)) || localisations.value[0]
    formulaire.value.localisation = zoneProposee ? String(zoneProposee.id) : ''
  } catch (error) {
    erreur.value = error.message
  } finally {
    chargement.value = false
  }
})

async function soumettre () {
  erreur.value = ''
  if (!formulaire.value.appareil) {
    erreur.value = 'Veuillez sélectionner le type d’appareil.'
    return
  }
  if (!formulaire.value.description.trim() || formulaire.value.description.trim().length < 10) {
    erreur.value = 'La description de la panne doit contenir au moins 10 caractères.'
    return
  }
  if (!formulaire.value.localisation) {
    erreur.value = 'Veuillez choisir votre zone de localisation.'
    return
  }
  if (adresseRequise.value && !adresseValide.value) {
    erreur.value = 'Indiquez votre adresse ou activez la géolocalisation pour une intervention à domicile.'
    return
  }
  if (!peutEnvoyer.value || envoi.value) return
  envoi.value = true
  try {
    await creerDemande({
      appareil: descriptionComplete.value,
      description_probleme: formulaire.value.description.trim(),
      localisation: Number(formulaire.value.localisation),
      mode_intervention: formulaire.value.mode_intervention,
      adresse_intervention: formulaire.value.adresse_intervention.trim(),
      latitude: positionGps.value ? Number(positionGps.value.latitude.toFixed(6)) : null,
      longitude: positionGps.value ? Number(positionGps.value.longitude.toFixed(6)) : null,
      ...(demandeIssueDiagnostic.value ? {
        specialite: diagnosticPourDemande.value.specialiteId,
        source: 'RECOMMANDATION_IA',
        diagnostic_ia: diagnosticPourDemande.value.resultat,
      } : { source: 'RECHERCHE' }),
      ...(reparateurSelectionne.value ? { reparateur: Number(reparateurSelectionne.value) } : {}),
    }, photos.value)
    sessionStorage.removeItem('reparsystem-diagnostic')
    succes.value = true
  } catch (error) {
    erreur.value = error.message
  } finally {
    envoi.value = false
  }
}

function activerLocalisation () {
  localisationErreur.value = ''
  if (!navigator.geolocation) {
    localisationErreur.value = 'La géolocalisation n’est pas disponible sur cet appareil.'
    return
  }
  localisationEnCours.value = true
  navigator.geolocation.getCurrentPosition(
    ({ coords }) => {
      positionGps.value = { latitude: coords.latitude, longitude: coords.longitude }
      localisationEnCours.value = false
    },
    () => {
      localisationErreur.value = 'Autorisez la localisation dans votre navigateur ou indiquez votre adresse manuellement.'
      localisationEnCours.value = false
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 },
  )
}

const ajouterPhotos = (event) => {
  const fichiers = Array.from(event.target.files || [])
  if (!fichiers.length) return

  const total = [...photos.value, ...fichiers]
  if (total.length > 3) {
    erreur.value = 'Vous pouvez joindre jusqu’à 3 photos maximum.'
    event.target.value = ''
    return
  }

  const previews = fichiers.map((fichier) => ({
    name: fichier.name,
    url: URL.createObjectURL(fichier),
  }))

  photoPreviews.value.push(...previews)
  photos.value = total
  erreur.value = ''
  event.target.value = ''
}

const retirerPhoto = (index) => {
  const photo = photoPreviews.value[index]
  if (photo?.url) URL.revokeObjectURL(photo.url)
  photos.value.splice(index, 1)
  photoPreviews.value.splice(index, 1)
}

const nomReparateur = computed(() => {
  const utilisateur = reparateur.value?.utilisateur_detail || {}
  return [utilisateur.prenom, utilisateur.nom].filter(Boolean).join(' ')
})
</script>

<template>
  <EntetePublic />
  <main class="request-page">
    <div class="request-wrap">
      <RouterLink class="back-link" :to="reparateur ? `/reparateurs/${reparateur.id}` : '/reparateurs'">← Retour</RouterLink>
      <section v-if="chargement" class="request-card loading">Préparation du formulaire…</section>
      <section v-else-if="succes" class="request-card confirmation" role="status">
        <span class="success-icon"><AppIcon name="check" :size="24" /></span>
        <p class="eyebrow">DEMANDE TRANSMISE</p>
        <h1>Votre demande d’intervention est envoyée</h1>
        <p v-if="nomReparateur">{{ nomReparateur }} pourra consulter votre panne et les informations d’intervention.</p>
        <p v-else>Les réparateurs correspondant à votre besoin pourront consulter votre demande.</p>
        <RouterLink class="submit-button" to="/">Retour à l’accueil</RouterLink>
      </section>
      <form v-else class="request-card" @submit.prevent="soumettre">
        <header class="form-heading">
          <h1>Demander une intervention</h1>
        </header>

        <p v-if="erreur" class="feedback error" role="alert">{{ erreur }}</p>
        <section v-if="!route.query.reparateur" class="form-section">
          <h2>Choisir un réparateur</h2>
          <label class="field-label" for="reparateur">À qui adresser votre demande ?</label>
          <select id="reparateur" v-model="reparateurSelectionne" class="text-input" required>
            <option disabled value="">Sélectionnez un réparateur vérifié</option>
            <option v-for="pro in reparateurs" :key="pro.id" :value="String(pro.id)">{{ [pro.utilisateur_detail?.prenom, pro.utilisateur_detail?.nom].filter(Boolean).join(' ') }} · {{ pro.specialites_detail?.map(item => item.nom).join(', ') || 'Réparateur' }}</option>
          </select>
          <small v-if="!reparateurs.length" class="helper">Aucun réparateur vérifié n’est disponible pour le moment.</small>
        </section>
        <section class="form-section">
          <h2>L’appareil à réparer</h2>
          <div class="device-carousel">
            <button class="device-scroll" type="button" aria-label="Défiler les appareils vers la gauche" @click="defilerAppareils(-1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg></button>
            <div ref="grilleAppareils" class="device-grid" role="group" aria-label="Type d’appareil">
              <button v-for="type in typesAppareils" :key="type" type="button" :class="['device-choice', { selected: formulaire.appareil === type }]" :aria-pressed="formulaire.appareil === type" @click="formulaire.appareil = type">
                <svg class="device-icon" viewBox="0 0 24 24" aria-hidden="true">
                  <template v-if="type === 'Smartphone'"><rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/></template>
                  <template v-else-if="type === 'Ordinateur'"><rect x="3" y="3" width="18" height="14" rx="2"/><path d="M2 21h20l-2-4H4l-2 4Z"/></template>
                  <template v-else-if="type === 'Tablette'"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M11 18h2"/></template>
                  <template v-else-if="type === 'Télévision'"><rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 22h8m-4-4v4"/></template>
                  <template v-else-if="type === 'Électroménager'"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 8h14m-10-3h.01M14 5h.01"/><circle cx="12" cy="15" r="4"/></template>
                  <template v-else><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></template>
                </svg>
                <span>{{ type }}</span>
              </button>
            </div>
            <button class="device-scroll" type="button" aria-label="Défiler les appareils vers la droite" @click="defilerAppareils(1)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg></button>
          </div>
          <label class="field-label" for="modele">Marque et modèle <span>(facultatif)</span></label>
          <input id="modele" v-model.trim="formulaire.modele" class="text-input" maxlength="80" placeholder="Ex. Samsung Galaxy S21">
        </section>

        <section class="form-section">
          <h2>La panne</h2>
          <label class="field-label" for="description">Que faut-il réparer ?</label>
          <textarea id="description" v-model.trim="formulaire.description" class="text-input" rows="5" maxlength="2000" required placeholder="Décrivez les symptômes, depuis quand le problème est apparu et ce que vous avez déjà essayé…"></textarea>
          <small class="helper">10 caractères minimum · {{ formulaire.description.length }}/2000</small>
        </section>

        <section class="form-section">
          <h2>Photos du problème</h2>
          <label class="field-label" for="photos">Joindre jusqu’à 3 photos</label>

          <label class="upload-area" for="photos">
            <input id="photos" type="file" accept="image/jpeg,image/png,image/webp" multiple @change="ajouterPhotos" class="hidden-file-input">
            <span class="upload-icon"><AppIcon name="camera" :size="20" /></span>
            <span class="upload-text">Ajouter des photos</span>
            <small>{{ photos.length }}/3 sélectionnées</small>
          </label>

          <div v-if="photoPreviews.length" class="photo-grid">
            <div v-for="(photo, index) in photoPreviews" :key="`${photo.name}-${index}`" class="photo-card">
              <img :src="photo.url" :alt="photo.name">
              <button type="button" class="remove-photo" @click="retirerPhoto(index)" aria-label="Retirer la photo">×</button>
            </div>
          </div>
        </section>

        <section class="form-section">
          <h2>Où souhaitez-vous l’intervention ?</h2>
          <label class="field-label" for="localisation">Ville / zone</label>
          <select id="localisation" v-model="formulaire.localisation" class="text-input" required>
            <option disabled value="">Sélectionnez votre zone</option>
            <option v-for="zone in localisations" :key="zone.id" :value="String(zone.id)">{{ [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(' · ') }}</option>
          </select>
          <div class="mode-grid" role="group" aria-label="Mode d’intervention">
            <button type="button" :class="['mode-choice', { selected: formulaire.mode_intervention === 'DOMICILE' }]" @click="formulaire.mode_intervention = 'DOMICILE'">À domicile</button>
            <button type="button" :class="['mode-choice', { selected: formulaire.mode_intervention === 'ATELIER' }]" @click="formulaire.mode_intervention = 'ATELIER'">À l’atelier du réparateur</button>
          </div>
          <template v-if="adresseRequise">
            <div class="location-control">
              <div>
                <strong>Indiquer ma position exacte</strong>
                <small>Autorisez la géolocalisation pour joindre vos coordonnées GPS à la demande.</small>
              </div>
              <button class="location-button" type="button" :disabled="localisationEnCours" @click="activerLocalisation">
                {{ localisationEnCours ? 'Localisation…' : positionGps ? 'Position activée' : 'Activer ma localisation' }} <AppIcon v-if="!localisationEnCours" :name="positionGps ? 'check' : 'locate'" :size="15" />
              </button>
            </div>
            <p v-if="positionGps" class="location-status" role="status">Position GPS enregistrée. Elle sera transmise uniquement au réparateur destinataire.</p>
            <p v-if="localisationErreur" class="feedback error" role="alert">{{ localisationErreur }}</p>
            <label class="field-label" for="adresse">Adresse ou repère</label>
            <input id="adresse" v-model.trim="formulaire.adresse_intervention" class="text-input" maxlength="255" :required="!positionGps" placeholder="Quartier, rue, repère…">
            <small class="helper">Adresse manuelle ou position GPS requise pour une intervention à domicile.</small>
          </template>
        </section>

        <button class="submit-button" type="submit" :disabled="envoi || !peutEnvoyer || !localisations.length || !reparateurSelectionne">
          {{ envoi ? 'Envoi en cours…' : 'Envoyer ma demande d’intervention' }} <AppIcon aria-hidden="true" name="arrow-right" :size="18" />
        </button>
      </form>
    </div>
  </main>
  <PiedDePage />
</template>

<style scoped>
.request-page{min-height:70vh;padding:42px 20px 76px;background:#f4f8f7;color:#102b3b}.request-wrap{width:min(100%,780px);margin:0 auto}.back-link{display:inline-block;margin:0 0 17px;color:#168273;text-decoration:none;font-size:13px;font-weight:700}.request-card{padding:38px 42px;border:1px solid #e0ebe7;border-radius:18px;background:#fff;box-shadow:0 18px 48px rgba(21,70,74,.09)}.form-heading{margin-bottom:30px}.eyebrow{color:#168273;font-size:10px;font-weight:800;letter-spacing:1.5px}.form-heading h1,.confirmation h1{margin:10px 0;color:#102b3b;font-size:clamp(26px,4vw,36px);letter-spacing:-.8px;line-height:1.12}.form-heading p,.confirmation>p{color:#718589;font-size:13px;line-height:1.6}.form-heading p strong{color:#168273}.form-section{padding:24px 0;border-top:1px solid #e8efec}.form-section h2{display:flex;align-items:center;gap:11px;margin:0 0 18px;color:#24434c;font-size:16px}.form-section h2 span{display:grid;width:28px;height:28px;place-items:center;border-radius:50%;background:#e7f5f0;color:#168273;font-size:10px}.device-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:19px}.device-choice,.mode-choice{min-height:45px;padding:10px;border:1px solid #dce8e4;border-radius:9px;background:#fbfdfc;color:#567078;font:inherit;font-size:12px;cursor:pointer}.device-choice.selected,.mode-choice.selected{border-color:#168273;background:#eef8f5;color:#087f70;font-weight:800}.field-label{display:block;margin:15px 0 8px;color:#284750;font-size:12px;font-weight:800}.field-label span{color:#8a9a9b;font-weight:400}.text-input{width:100%;box-sizing:border-box;padding:13px 14px;border:1px solid #dbe7e4;border-radius:9px;background:#fbfdfc;color:#284750;font:inherit;font-size:13px;outline:none}.text-input:focus{border-color:#168273;box-shadow:0 0 0 3px #16827318}.text-input textarea,textarea.text-input{resize:vertical}.helper{display:block;margin-top:7px;color:#8a9a9b;font-size:10px}.upload-area{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:18px 16px;border:1.5px dashed #a7d9cf;border-radius:14px;background:linear-gradient(135deg,#f4fbf8,#eef8f5);color:#0d5d56;cursor:pointer;transition:transform .2s ease,border-color .2s ease,box-shadow .2s ease}.upload-area:hover{transform:translateY(-2px);border-color:#5db3a2;box-shadow:0 10px 20px rgba(22,130,115,.08)}.upload-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#dff4ef;color:#0f6d60}.upload-text{font-size:14px;font-weight:800}.upload-area small{color:#61868d;font-size:11px}.hidden-file-input{display:none}.photo-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:16px}.photo-card{position:relative;overflow:hidden;border-radius:12px;border:1px solid #dfece8;background:#f7fbfa;aspect-ratio:1/1;box-shadow:0 8px 18px rgba(19,73,69,.06)}.photo-card img{display:block;width:100%;height:100%;object-fit:cover}.remove-photo{position:absolute;top:8px;right:8px;display:grid;place-items:center;width:28px;height:28px;border:0;border-radius:50%;background:rgba(8,27,32,.7);color:#fff;font-size:18px;line-height:1;cursor:pointer}.mode-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}.privacy-note{margin:6px 0 16px;padding:13px 15px;border-radius:9px;background:#f1f8f6;color:#65807f;font-size:11px;line-height:1.55}.submit-button{display:flex;width:100%;min-height:50px;align-items:center;justify-content:center;gap:10px;border:0;border-radius:9px;background:#168273;color:#fff;text-decoration:none;font:inherit;font-size:13px;font-weight:800;cursor:pointer;transition:background .2s,transform .2s}.submit-button:hover{background:#0d685e;transform:translateY(-1px)}.submit-button:disabled{opacity:.55;cursor:not-allowed;transform:none}.feedback{padding:12px 14px;border-radius:8px;font-size:12px}.error{background:#fff0f0;color:#b43c46}.loading,.confirmation{text-align:center}.confirmation{padding-top:54px;padding-bottom:54px}.success-icon{display:grid;width:52px;height:52px;margin:0 auto 16px;place-items:center;border-radius:50%;background:#e5f6ef;color:#168273;font-size:25px;font-weight:800}.confirmation .submit-button{margin-top:22px}@media(max-width:600px){.request-page{padding:28px 14px 54px}.request-card{padding:28px 19px;border-radius:14px}.device-grid{grid-template-columns:repeat(2,1fr)}.mode-grid{grid-template-columns:1fr}.form-section{padding:20px 0}}
/* Reprend l’ambiance de la page Diagnostic tout en gardant le formulaire lisible. */
.request-page{background:radial-gradient(circle at 50% 0%,#12395a 0,#071d35 42%,#051426 100%);padding-top:48px}.request-wrap{width:min(100%,1040px)}.request-card{padding:44px 40px 38px;border-radius:18px;box-shadow:0 25px 65px rgba(0,0,0,.28)}.form-heading{margin-bottom:38px}.form-heading h1{font-size:clamp(30px,4vw,42px);letter-spacing:-1.2px}.form-section{padding:27px 0;border-color:#edf2f0}.form-section h2{font-size:17px}.device-choice,.mode-choice{min-height:58px;transition:background .2s ease,border-color .2s ease,transform .2s ease}.device-choice:hover,.mode-choice:hover{transform:translateY(-2px)}.location-control{display:flex;align-items:center;justify-content:space-between;gap:18px;margin-top:21px;padding:17px;border:1px solid #d9ebe5;border-radius:12px;background:linear-gradient(145deg,#f7fcfa,#eef8f5)}.location-control>div{display:grid;gap:6px}.location-control strong{color:#24434c;font-size:12px}.location-control small{color:#809395;font-size:11px;line-height:1.5}.location-button{flex:0 0 auto;padding:12px 15px;border:1px solid #b8d8d0;border-radius:9px;background:#fff;color:#168273;font:inherit;font-size:11px;font-weight:800;cursor:pointer;transition:transform .2s ease,box-shadow .2s ease}.location-button:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 18px rgba(22,130,115,.12)}.location-button:disabled{opacity:.6;cursor:wait}.location-status{margin:10px 0 0;color:#147665;font-size:11px;line-height:1.5}.privacy-note{margin:10px 0 20px;padding:13px 15px;border-radius:10px;background:#f5faf8;color:#718589;font-size:11px;line-height:1.6}.submit-button{max-width:640px;margin:0 auto;border-radius:9px;box-shadow:0 9px 18px rgba(22,130,115,.16);transition:transform .2s ease,box-shadow .2s ease}.submit-button:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 13px 24px rgba(22,130,115,.22)}.submit-button:disabled{opacity:.58;cursor:not-allowed}.back-link{color:#bce3d9}.back-link:hover{text-decoration:underline}.text-input:focus-visible,.location-button:focus-visible,.submit-button:focus-visible,.device-choice:focus-visible,.mode-choice:focus-visible{outline:3px solid #54c8b5;outline-offset:2px}@media(max-width:600px){.request-page{padding-top:32px}.request-card{padding:30px 20px}.location-control{align-items:stretch;flex-direction:column}.location-button{width:100%}}
.device-carousel{display:grid;grid-template-columns:34px minmax(0,1fr) 34px;align-items:center;gap:12px;margin-bottom:25px}
.device-grid{display:flex;min-width:0;gap:18px;margin:0;overflow-x:auto;scrollbar-width:none;scroll-snap-type:x mandatory;scroll-behavior:smooth}
.device-grid::-webkit-scrollbar{display:none}
.device-choice{display:flex;flex:0 0 calc((100% - 36px)/4);min-width:120px;min-height:102px;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:14px 10px;scroll-snap-align:start}
.device-icon{width:26px;height:26px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.device-scroll{display:grid;width:34px;height:34px;place-items:center;border:1px solid #b8d8d0;border-radius:50%;background:#fff;color:#168273;cursor:pointer;transition:background .18s ease,color .18s ease,transform .18s ease}
.device-scroll:hover{transform:scale(1.06);background:#168273;color:#fff}
.device-scroll svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
@media(max-width:650px){.device-carousel{grid-template-columns:30px minmax(0,1fr) 30px;gap:6px}.device-scroll{width:30px;height:30px}.device-choice{flex-basis:calc((100% - 12px)/2);min-width:118px;min-height:90px}}
.request-page{min-height:calc(100vh - 72px)}
@media(max-width:800px){.request-page{min-height:calc(100vh - 120px)}}
</style>
