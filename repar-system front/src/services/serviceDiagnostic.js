import { api } from './api'
import { convertirAudioEnWav } from './audioWav'

const listeDepuisReponse = (reponse) => Array.isArray(reponse) ? reponse : reponse.results || []

const correspond = (valeur, cible) => String(valeur || '').toLocaleLowerCase().trim() === String(cible || '').toLocaleLowerCase().trim()

export async function analyserDiagnostic (donnees, photos = []) {
  const body = photos.length
    ? (() => {
        const formulaire = new FormData()
        Object.entries(donnees).forEach(([cle, valeur]) => {
          if (valeur !== null && valeur !== undefined && valeur !== '') formulaire.append(cle, valeur)
        })
        photos.forEach((photo) => formulaire.append('photos', photo))
        return formulaire
      })()
    : JSON.stringify(donnees)

  return api('/ia/diagnostic/', {
    method: 'POST',
    body,
  })
}

export async function traduireDescription (description) {
  return api('/ia/traduction/', {
    method: 'POST',
    body: JSON.stringify({ description }),
  })
}

export async function transcrireAudio (audio, language = 'auto') {
  const compatible = await convertirAudioEnWav(audio)
  const donnees = new FormData()
  donnees.append('audio', compatible, 'description.wav')
  donnees.append('language', language)
  return api('/ia/transcription/', { method: 'POST', body: donnees })
}

export async function chargerReparateursProches ({ latitude, longitude, specialite }) {
  const params = new URLSearchParams({ latitude: String(latitude), longitude: String(longitude) })
  if (specialite) params.set('specialite', String(specialite))
  return api(`/reparateurs/recommandations/?${params.toString()}`)
}

export async function chargerReferentielsDiagnostic () {
  const [localisations, specialites] = await Promise.all([
    api('/localisations/'),
    api('/specialites/'),
  ])
  return {
    localisations: listeDepuisReponse(localisations),
    specialites: listeDepuisReponse(specialites),
  }
}

export function trouverSpecialite (specialites, nom) {
  return specialites.find((item) => correspond(item.nom, nom))
    || specialites.find((item) => String(item.nom || '').toLocaleLowerCase().includes(String(nom || '').toLocaleLowerCase()))
}
