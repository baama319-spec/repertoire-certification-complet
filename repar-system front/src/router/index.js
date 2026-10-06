import { createRouter, createWebHistory } from 'vue-router'
import Accueil from '../views/public/Accueil.vue'
import TrouverReparateur from '../views/public/TrouverReparateur.vue'
import ProfilReparateurPublic from '../views/public/ProfilReparateurPublic.vue'
import DemandesReparateur from '../views/reparateur/DemandesReparateur.vue'
import Realisations from '../views/reparateur/Realisations.vue'
import AvisClients from '../views/reparateur/AvisClients.vue'
import MonProfilReparateur from '../views/reparateur/MonProfilReparateur.vue'
import TableauDeBordAdmin from '../views/administrateur/TableauDeBordAdmin.vue'
import GestionCategories from '../views/administrateur/GestionCategories.vue'
import GestionZones from '../views/administrateur/GestionZones.vue'
import GestionDemandes from '../views/administrateur/GestionDemandes.vue'
import GestionReparateurs from '../views/administrateur/GestionReparateurs.vue'
import GestionClients from '../views/administrateur/GestionClients.vue'
import Connexion from '../views/authentification/Connexion.vue'
import Inscription from '../views/authentification/Inscription.vue'
import MesDemandes from '../views/client/MesDemandes.vue'
import MonProfil from '../views/client/MonProfil.vue'
import MesAvis from '../views/client/MesAvis.vue'
import DevenirReparateur from '../views/public/DevenirReparateur.vue'
import Diagnostic from '../views/public/Diagnostic.vue'
import DemandeReparation from '../views/public/DemandeReparation.vue'
import { routeAccueilUtilisateur } from '../services/serviceAuthentification'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'accueil', component: Accueil },
    { path: '/reparateurs', name: 'trouver-reparateur', component: TrouverReparateur },
    { path: '/diagnostic', name: 'diagnostic', component: Diagnostic },
    { path: '/demande-reparation', name: 'demande-reparation', component: DemandeReparation },
    { path: '/reparateurs/:slug', name: 'profil-reparateur', component: ProfilReparateurPublic, props: true },
    { path: '/devenir-reparateur', name: 'devenir-reparateur', component: DevenirReparateur },
    { path: '/pro', redirect: '/pro/demandes' },
    { path: '/pro/demandes', name: 'demandes-reparateur', component: DemandesReparateur },
    { path: '/pro/realisations', name: 'realisations-reparateur', component: Realisations },
    { path: '/pro/avis', name: 'avis-clients-reparateur', component: AvisClients },
    { path: '/pro/profil', name: 'profil-reparateur-pro', component: MonProfilReparateur },
    { path: '/admin', name: 'admin-dashboard', component: TableauDeBordAdmin },
    { path: '/admin/categories', name: 'admin-categories', component: GestionCategories },
    { path: '/admin/zones', name: 'admin-zones', component: GestionZones },
    { path: '/admin/demandes', name: 'admin-demandes', component: GestionDemandes },
    { path: '/admin/reparateurs', name: 'admin-reparateurs', component: GestionReparateurs },
    { path: '/admin/clients', name: 'admin-clients', component: GestionClients },
    { path: '/connexion', name: 'connexion', component: Connexion },
    { path: '/inscription', name: 'inscription', component: Inscription },
    { path: '/client/demandes', name: 'mes-demandes-client', component: MesDemandes },
    { path: '/client/profil', name: 'profil-client', component: MonProfil },
    { path: '/client/avis', name: 'mes-avis-client', component: MesAvis },
  ],
})

const lireUtilisateur = () => {
  if (!localStorage.getItem('reparsystem-token') && !sessionStorage.getItem('reparsystem-token')) return null
  const brut = localStorage.getItem('reparsystem-utilisateur') || sessionStorage.getItem('reparsystem-utilisateur')
  try { return brut ? JSON.parse(brut) : null } catch (_) { return null }
}

router.beforeEach((to) => {
  const utilisateur = lireUtilisateur()
  const pageSansFooter = ['/connexion', '/inscription'].includes(to.path)
  const footerPublicVisible = ['/', '/reparateurs'].includes(to.path)
  document.body.classList.toggle('page-no-footer', Boolean(utilisateur) && !pageSansFooter && !footerPublicVisible)

  if (utilisateur && ['/connexion', '/inscription'].includes(to.path)) {
    return routeAccueilUtilisateur(utilisateur)
  }

  if (to.path.startsWith('/admin') && utilisateur?.role !== 'ADMINISTRATEUR') {
    return { path: '/connexion', query: { redirection: to.fullPath } }
  }
  if (to.path.startsWith('/client') && utilisateur?.role !== 'CLIENT') {
    return { path: '/connexion', query: { redirection: to.fullPath } }
  }
  if (['/diagnostic', '/demande-reparation'].includes(to.path) && utilisateur?.role !== 'CLIENT') {
    return { path: '/connexion', query: { redirection: to.fullPath } }
  }
  const reparateurValide = utilisateur?.actif !== false && utilisateur?.profil_reparateur?.statut_verification === 'VALIDEE'
  if (to.path.startsWith('/pro') && !reparateurValide) {
    return utilisateur
      ? { path: '/devenir-reparateur', query: { statut: 'validation-requise' } }
      : { path: '/connexion', query: { redirection: to.fullPath } }
  }
})

export default router
