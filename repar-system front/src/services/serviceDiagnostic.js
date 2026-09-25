import { api } from './api'

const listeDepuisReponse = (reponse) => Array.isArray(reponse) ? reponse : reponse.results || []

const correspond = (valeur, cible) => String(valeur || '').toLocaleLowerCase().trim() === String(cible || '').toLocaleLowerCase().trim()

export async function analyserDiagnostic (donnees) {
  return api('/ia/diagnostic/', {
    method: 'POST',
    body: JSON.stringify(donnees),
  })
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

export function trouverLocalisation (localisations, ville, quartier = '') {
  return localisations.find((item) => correspond(item.ville, ville) && quartier && correspond(item.quartier, quartier))
    || localisations.find((item) => correspond(item.ville, ville))
}

export function trouverSpecialite (specialites, nom) {
  return specialites.find((item) => correspond(item.nom, nom))
    || specialites.find((item) => String(item.nom || '').toLocaleLowerCase().includes(String(nom || '').toLocaleLowerCase()))
}

export async function creerDemandeDepuisDiagnostic ({ description, localisation, specialite }) {
  return api('/demandes/', {
    method: 'POST',
    body: JSON.stringify({
      description_probleme: description,
      localisation,
      ...(specialite ? { specialite } : {}),
      source: 'RECOMMANDATION_IA',
    }),
  })
}
