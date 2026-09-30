import { api } from './api'
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
export const creerDemande = async (donnees) => api('/demandes/', { method: 'POST', body: JSON.stringify(donnees) })
export const accepterDemande = async (id) => api(`/demandes/${id}/accepter/`, { method: 'POST' })
export const refuserDemande = async (id) => api(`/demandes/${id}/refuser/`, { method: 'POST' })

// Compatibilité avec l'écran administrateur existant, qui sera migré vers les
// fonctions asynchrones ci-dessus dans une évolution séparée.
export const useDemandes = () => {
  const demandes = ref([])
  const remove = id => { demandes.value = demandes.value.filter(demande => demande.id !== id) }
  return { demandes, remove }
}
