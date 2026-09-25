import { ref } from 'vue'
import { api } from './api'

const categories = ref([])
const convertir = (categorie) => ({ id: categorie.id, name: categorie.nom, description: categorie.description, photo: categorie.photo || '', active: categorie.actif, repairers: categorie.reparateurs_count || 0, icon: '✦', color: 'blue' })

export function useCategories () {
  const charger = async () => {
    const data = await api('/specialites/')
    categories.value = (data.results || data).map(convertir)
  }
  const create = async ({ name, description, photo, active }) => {
    const donnees = new FormData()
    donnees.append('nom', name)
    donnees.append('description', description)
    donnees.append('actif', active)
    if (photo) donnees.append('photo', photo)
    const categorie = await api('/specialites/', { method: 'POST', body: donnees })
    categories.value.push(convertir(categorie))
  }
  const update = async (category) => {
    const donnees = new FormData()
    donnees.append('nom', category.name)
    donnees.append('description', category.description)
    donnees.append('actif', category.active)
    if (category.photo instanceof File) donnees.append('photo', category.photo)
    const categorie = await api(`/specialites/${category.id}/`, { method: 'PATCH', body: donnees })
    const index = categories.value.findIndex(({ id }) => id === category.id)
    if (index !== -1) categories.value[index] = convertir(categorie)
  }
  const remove = async (id) => {
    await api(`/specialites/${id}/`, { method: 'DELETE' })
    categories.value = categories.value.filter((category) => category.id !== id)
  }
  return { categories, charger, create, update, remove }
}
