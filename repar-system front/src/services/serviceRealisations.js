import { api } from './api'
export const chargerRealisations = async (reparateurId = '') => {
  const data = await api(`/realisations/${reparateurId ? `?reparateur=${reparateurId}` : ''}`)
  return data.results || data
}
export const chargerMesRealisations = async () => {
  const data = await api('/realisations/mes/')
  return data.results || data
}
export const ajouterRealisation = ({ titre, description, specialite, photoAvant, photoApres }) => {
  return api('/realisations/', { method: 'POST', body: formDataRealisation({ titre, description, specialite, photoAvant, photoApres }) })
}

export const modifierRealisation = (id, { titre, description, specialite, photoAvant, photoApres }) =>
  api(`/realisations/${id}/`, { method: 'PATCH', body: formDataRealisation({ titre, description, specialite, photoAvant, photoApres }) })

const formDataRealisation = ({ titre, description, specialite, photoAvant, photoApres }) => {
  const donnees = new FormData()
  Object.entries({ titre, description, specialite }).forEach(([cle, valeur]) => donnees.append(cle, valeur))
  if (photoAvant) donnees.append('photo_avant', photoAvant)
  if (photoApres) donnees.append('photo_apres', photoApres)
  return donnees
}

export const supprimerRealisation = id => api(`/realisations/${id}/`, { method: 'DELETE' })
