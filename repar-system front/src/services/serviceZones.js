import { ref } from 'vue'
import { api } from './api'

const zones = ref([])
const convertir = (zone) => ({ id: zone.id, city: zone.ville, districts: zone.quartier, technicians: zone.reparateurs_count || 0, active: zone.actif })

export function useZones () {
  const charger = async () => {
    const data = await api('/localisations/')
    zones.value = (data.results || data).map(convertir)
  }
  const create = async ({ city, districts, active }) => {
    const zone = await api('/localisations/', { method: 'POST', body: JSON.stringify({ nom: city, ville: city, quartier: districts, adresse: districts, actif: active }) })
    zones.value.push(convertir(zone))
  }
  const update = async (zone) => {
    const resultat = await api(`/localisations/${zone.id}/`, { method: 'PATCH', body: JSON.stringify({ nom: zone.city, ville: zone.city, quartier: zone.districts, adresse: zone.districts, actif: zone.active }) })
    const index = zones.value.findIndex(({ id }) => id === zone.id)
    if (index !== -1) zones.value[index] = convertir(resultat)
  }
  const remove = async (id) => {
    await api(`/localisations/${id}/`, { method: 'DELETE' })
    zones.value = zones.value.filter((zone) => zone.id !== id)
  }
  return { zones, charger, create, update, remove }
}
