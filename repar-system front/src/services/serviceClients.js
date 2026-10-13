import { ref } from 'vue'
import { api } from './api'

const clients = ref([])
const photoDefaut = 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=140&q=80'

const convertir = (client) => {
  const utilisateur = client.utilisateur_detail || {}
  const zone = client.zone_residence_detail || {}
  const nom = [utilisateur.prenom, utilisateur.nom].filter(Boolean).join(' ') || 'Client'
  const adresse = [client.adresse_principale, zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ') || 'Adresse non renseignée'
  return {
    id: client.id,
    name: nom,
    phone: utilisateur.telephone || 'Non renseigné',
    email: utilisateur.email || '',
    address: adresse,
    requests: 0,
    history: [],
    status: utilisateur.actif === false ? 'Bloqué' : 'Actif',
    image: utilisateur.photo_profil || photoDefaut,
    actif: utilisateur.actif !== false,
    dateInscription: utilisateur.date_inscription || null,
    raw: client,
  }
}

const mapperHistorique = (demande) => {
  const statut = demande.statut || 'EN_ATTENTE'
  const specialite = demande.specialite_detail || {}
  const reparateur = demande.reparateur_detail || {}
  const date = demande.date_creation || null

  return {
    id: demande.id,
    date,
    device: demande.appareil || specialite.nom || 'Réparation',
    issue: demande.description_probleme || 'Aucune description fournie.',
    pro: reparateur.nom || 'À attribuer',
    status: statut,
    icon: statut === 'ACCEPTEE' ? 'check-circle' : 'wrench',
  }
}

export function useClients () {
  const charger = async () => {
    const [clientsData, demandesData] = await Promise.all([
      api('/clients/'),
      api('/demandes/'),
    ])

    const demandes = demandesData.results || demandesData || []
    const compteDemandes = new Map()
    const historiqueParClient = new Map()

    for (const demande of demandes) {
      const clientId = Number(demande.client_detail?.id ?? demande.client)
      if (!clientId) continue

      compteDemandes.set(clientId, (compteDemandes.get(clientId) || 0) + 1)
      const historique = historiqueParClient.get(clientId) || []
      historique.push(mapperHistorique(demande))
      historiqueParClient.set(clientId, historique)
    }

    clients.value = (clientsData.results || clientsData || []).map((client) => {
      const item = convertir(client)
      const id = Number(item.id)
      item.requests = compteDemandes.get(id) || 0
      item.history = historiqueParClient.get(id) || []
      return item
    })
  }

  const toggle = async (client) => {
    if (!client?.id) return null
    const devraBloquer = client.status !== 'Bloqué'
    const resultat = await api(`/clients/${client.id}/bloquer/`, {
      method: 'POST',
      body: JSON.stringify({ bloquer: devraBloquer }),
    })

    const mapped = convertir(resultat)
    const index = clients.value.findIndex(item => item.id === mapped.id)
    if (index !== -1) {
      mapped.requests = clients.value[index].requests
      clients.value[index] = mapped
    }

    return mapped
  }

  return { clients, charger, toggle }
}
