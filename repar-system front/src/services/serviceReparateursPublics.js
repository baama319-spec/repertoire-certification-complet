import { api } from './api'

const imageDefaut = 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=700&q=85'
const slug = texte => (texte || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
export const chargerReparateursPublics = async (coordonnees = {}) => {
  const params = new URLSearchParams()
  if (coordonnees.latitude != null && coordonnees.longitude != null) {
    params.set('latitude', coordonnees.latitude)
    params.set('longitude', coordonnees.longitude)
  }
  const data = await api(`/reparateurs/${params.toString() ? `?${params}` : ''}`)
  return (data.results || data).map(profil => {
    const utilisateur = profil.utilisateur_detail || {}
    const nom = [utilisateur.prenom, utilisateur.nom].filter(Boolean).join(' ') || 'Réparateur'
    const specialites = (profil.specialites_detail || []).map(item => item.nom)
    const zonesDetail = profil.zones_intervention_detail || []
    const zones = zonesDetail.map(item => [item.ville, item.quartier || item.nom].filter(Boolean).join(', '))
    const latitude = Number(profil.latitude)
    const longitude = Number(profil.longitude)
    const positionValide = Number.isFinite(latitude) && Number.isFinite(longitude)
    return { id: profil.id, slug: String(profil.id), name: nom, company: 'Réparateur vérifié', specialty: specialites[0] || 'Réparation', tags: specialites, location: zones[0] || 'Zone non renseignée', image: utilisateur.photo_profil || imageDefaut, badge: 'CERTIFIÉ', score: '—', distanceKm: profil.distance_km, lat: positionValide ? latitude : null, lon: positionValide ? longitude : null, profil }
  })
}
export const slugReparateur = slug