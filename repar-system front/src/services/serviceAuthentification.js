import { ref } from 'vue'
import { api } from './api'

const lireUtilisateurStocke = () => {
  if (!localStorage.getItem('reparsystem-token') && !sessionStorage.getItem('reparsystem-token')) return null
  try {
    return JSON.parse(localStorage.getItem('reparsystem-utilisateur') || sessionStorage.getItem('reparsystem-utilisateur') || 'null')
  } catch (_) {
    return null
  }
}

const utilisateur = ref(lireUtilisateurStocke())

export const routeAccueilUtilisateur = (compte = utilisateur.value) => {
  if (compte?.role === 'ADMINISTRATEUR') return '/admin'
  if (compte?.role === 'REPARATEUR') return '/pro/demandes'
  return '/client/demandes'
}

export const effacerSessionLocale = () => {
  utilisateur.value = null
  localStorage.removeItem('reparsystem-token')
  localStorage.removeItem('reparsystem-utilisateur')
  sessionStorage.removeItem('reparsystem-token')
  sessionStorage.removeItem('reparsystem-utilisateur')
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (['reparsystem-token', 'reparsystem-utilisateur'].includes(event.key)) {
      utilisateur.value = lireUtilisateurStocke()
    }
  })
  window.addEventListener('reparsystem:session-expired', effacerSessionLocale)
}

const memoriserSession = (data) => {
  utilisateur.value = data.utilisateur
  sessionStorage.removeItem('reparsystem-token')
  sessionStorage.removeItem('reparsystem-utilisateur')
  localStorage.setItem('reparsystem-token', data.token)
  localStorage.setItem('reparsystem-utilisateur', JSON.stringify(data.utilisateur))
}

const conserverSession = (data) => {
  utilisateur.value = data.utilisateur
  localStorage.removeItem('reparsystem-token')
  localStorage.removeItem('reparsystem-utilisateur')
  sessionStorage.setItem('reparsystem-token', data.token)
  sessionStorage.setItem('reparsystem-utilisateur', JSON.stringify(data.utilisateur))
}

  const enregistrerUtilisateur = (donnees) => {
  utilisateur.value = donnees
  const cle = localStorage.getItem('reparsystem-token') ? localStorage : sessionStorage
  cle.setItem('reparsystem-utilisateur', JSON.stringify(donnees))
}

export function useAuthentification () {
  const connecter = async ({ email, password, remember = true }) => {
    const data = await api('/utilisateurs/connexion/', { method: 'POST', body: JSON.stringify({ email, password }) })
    if (remember) memoriserSession(data)
    else conserverSession(data)
    return data.utilisateur
  }
  const inscrire = async (payload) => {
    const data = await api('/utilisateurs/inscription/', { method: 'POST', body: JSON.stringify(payload) })
    return data.utilisateur
  }
  const mettreAJourProfil = async (id, donnees) => {
    const resultat = await api(`/utilisateurs/${id}/`, { method: 'PATCH', body: donnees })
    enregistrerUtilisateur(resultat)
    return resultat
  }
  const changerMotDePasse = async (donnees) => {
    const resultat = await api('/utilisateurs/changer_mot_de_passe/', { method: 'POST', body: JSON.stringify(donnees) })
    const cle = localStorage.getItem('reparsystem-token') ? localStorage : sessionStorage
    cle.setItem('reparsystem-token', resultat.token)
    return resultat
  }
  const deconnecter = async () => {
    try {
      // L'invalidation serveur évite qu'un token conservé soit réutilisé.
      await api('/utilisateurs/deconnexion/', { method: 'POST' })
    } catch (_) {
      // La session locale doit tout de même être fermée si le serveur est indisponible.
    } finally { effacerSessionLocale() }
  }
  return { utilisateur, connecter, inscrire, mettreAJourProfil, changerMotDePasse, deconnecter, enregistrerUtilisateur }
}
