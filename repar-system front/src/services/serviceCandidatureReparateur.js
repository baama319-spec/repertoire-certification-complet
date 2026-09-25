import { api } from './api'

export const chargerCandidature = async () => (await api('/reparateurs/candidature/')).profil

export const envoyerCandidature = async (donnees) => {
  const profil = await api('/reparateurs/candidature/', {
    method: 'POST', body: JSON.stringify(donnees),
  })
  return profil.profil
}
