import { api } from './api'

export async function chargerStatistiquesAdministration () {
  return api('/demandes/statistiques/')
}
import { ref } from 'vue'

const liste = reponse => Array.isArray(reponse) ? reponse : reponse.results || []

export const chargerDemandes = async ({ contexte } = {}) => {
  const demandes = []
  let page = 1
  let pagesSuivantes = true

  while (pagesSuivantes) {
    const params = new URLSearchParams({ page: String(page) })
    if (contexte) params.set('contexte', contexte)
    const reponse = await api(`/demandes/?${params.toString()}`)
    if (Array.isArray(reponse)) return reponse

    demandes.push(...liste(reponse))
    pagesSuivantes = Boolean(reponse.next)
    page += 1
  }

  return demandes
}

export async function chargerDemandesAdministration () {
  const [demandes, statistiques] = await Promise.all([
    chargerDemandes(),
    chargerStatistiquesAdministration(),
  ])
  return { demandes, statistiques }
}

export const supprimerDemandeAdministration = async id => {
  await api(`/demandes/${id}/`, { method: 'DELETE' })
}

const preparerFormDataDemande = (donnees, photos = []) => {
  const formData = new FormData()
  Object.entries(donnees).forEach(([cle, valeur]) => {
    if (valeur === null || valeur === undefined || valeur === '') return
    formData.append(cle, valeur)
  })
  photos.slice(0, 3).forEach((fichier) => {
    if (fichier instanceof File) formData.append('photos', fichier)
  })
  return formData
}

export const creerDemande = async (donnees, photos = []) => api('/demandes/', {
  method: 'POST',
  body: preparerFormDataDemande(donnees, photos),
})
export const annulerDemandeClient = async id => api(`/demandes/${id}/annuler/`, { method: 'POST' })
export const accepterDemande = async (id) => api(`/demandes/${id}/accepter/`, { method: 'POST' })
export const refuserDemande = async (id) => api(`/demandes/${id}/refuser/`, { method: 'POST' })

// Compatibilité avec l'écran administrateur existant, qui sera migré vers les
// fonctions asynchrones ci-dessus dans une évolution séparée.
export const useDemandes = () => {
  const demandes = ref([])
  const remove = id => { demandes.value = demandes.value.filter(demande => demande.id !== id) }
  return { demandes, remove }
}
