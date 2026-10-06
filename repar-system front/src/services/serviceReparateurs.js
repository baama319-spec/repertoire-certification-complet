import { ref } from 'vue'
import { api } from './api'

const reparateurs = ref([])
const photoDefaut = 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=100&q=80'
const libelleZone = (zone) => [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ')
const statut = (profil) => {
  if (profil.utilisateur_detail?.actif === false) return 'Compte bloqué'
  return profil.profil_verifie ? 'Certifié Pro' : ({ EN_ATTENTE: 'En attente', REFUSEE: 'Refusée', VALIDEE: 'Validée' }[profil.statut_verification] || 'En attente')
}
const convertir = (profil) => ({
  id: profil.id, name: [profil.utilisateur_detail?.prenom, profil.utilisateur_detail?.nom].filter(Boolean).join(' '),
  phone: profil.utilisateur_detail?.telephone || 'Non renseigné', email: profil.utilisateur_detail?.email || '',
  image: profil.utilisateur_detail?.photo_profil || photoDefaut,
  carteIdentite: profil.photo_carte_identite || '',
  documents: (profil.documents_detail || []).map((document) => ({
    id: document.id,
    type: document.type_document || 'AUTRE',
    document: document.document || '',
    nomFichier: document.nom_fichier || 'Document joint',
  })),
  specialties: (profil.specialites_detail || []).map(({ nom }) => nom), zones: (profil.zones_intervention_detail || []).map(libelleZone),
  experience: profil.annee_experience, description: profil.description, status: statut(profil), statutVerification: profil.statut_verification, profilVerifie: profil.profil_verifie, estBloque: profil.utilisateur_detail?.actif === false, motifRefus: profil.motif_refus || '',
})

export function useReparateurs () {
  const charger = async () => { const data = await api('/reparateurs/'); reparateurs.value = (data.results || data).map(convertir) }
  const verifier = async (reparateur, statutVerification, motifRefus = '') => {
    const resultat = await api(`/reparateurs/${reparateur.id}/verifier/`, { method: 'POST', body: JSON.stringify({ statut_verification: statutVerification, motif_refus: motifRefus }) })
    const index = reparateurs.value.findIndex(({ id }) => id === reparateur.id)
    if (index !== -1) reparateurs.value[index] = convertir(resultat)
    return reparateurs.value[index]
  }
  const certifierPro = async (reparateur) => {
    const resultat = await api(`/reparateurs/${reparateur.id}/certifier_pro/`, { method: 'POST' })
    const index = reparateurs.value.findIndex(({ id }) => id === reparateur.id)
    if (index !== -1) reparateurs.value[index] = convertir(resultat)
    return reparateurs.value[index]
  }
  const bloquer = async (reparateur, doitBloquer) => {
    const resultat = await api(`/reparateurs/${reparateur.id}/bloquer/`, { method: 'POST', body: JSON.stringify({ bloquer: doitBloquer }) })
    const index = reparateurs.value.findIndex(({ id }) => id === reparateur.id)
    if (index !== -1) reparateurs.value[index] = convertir(resultat)
    return reparateurs.value[index]
  }
  return { reparateurs, charger, verifier, certifierPro, bloquer }
}
