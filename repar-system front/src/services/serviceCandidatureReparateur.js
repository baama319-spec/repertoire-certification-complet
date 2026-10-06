import { api } from './api'

const preparerFormData = (donnees) => {
  const formData = new FormData()
  Object.entries(donnees).forEach(([cle, valeur]) => {
    if (valeur === null || valeur === undefined || valeur === '') return
    if (cle === 'specialites' || cle === 'zones_intervention') {
      if (Array.isArray(valeur)) {
        valeur.forEach((item) => formData.append(cle, item))
      }
      return
    }
    if (cle === 'documents') {
      if (Array.isArray(valeur)) {
        valeur.forEach((document) => {
          if (document && document.file) {
            formData.append('documents', document.file)
            formData.append('document_types', document.type || 'AUTRE')
          }
        })
      }
      return
    }
    if (cle === 'photo_carte_identite' && valeur instanceof File) {
      formData.append(cle, valeur)
      return
    }
    formData.append(cle, valeur)
  })
  return formData
}

export const chargerCandidature = async () => (await api('/reparateurs/candidature/')).profil

export const envoyerCandidature = async (donnees) => {
  const profil = await api('/reparateurs/candidature/', {
    method: 'POST', body: preparerFormData(donnees),
  })
  return profil.profil
}
