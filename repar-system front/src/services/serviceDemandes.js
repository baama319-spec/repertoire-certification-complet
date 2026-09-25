import { ref } from 'vue'
const demandes = ref([
  { id: '#D-2026-089', date: '10/09/2026', time: '14:32', client: 'Mamadou Fall', phone: '+221 77 123 45 67', zone: 'Dakar, Plateau', device: 'Smartphone', issue: 'Écran brisé', icon: '▯', status: 'En attente' },
  { id: '#D-2026-088', date: '09/09/2026', time: '11:20', client: 'Fatou Cissé', phone: '+221 77 456 78 90', zone: 'Dakar, Liberté 6', device: 'Lave-linge', issue: 'Pompe bloquée', icon: '▣', status: 'Acceptée' },
  { id: '#D-2026-087', date: '08/09/2026', time: '16:45', client: 'Omar Ndiaye', phone: '+221 77 888 99 00', zone: 'Dakar, Ngor', device: 'PC Portable', issue: 'Surchauffe', icon: '▱', status: 'Terminée' },
])
export function useDemandes() { const remove = (id) => { demandes.value = demandes.value.filter((demande) => demande.id !== id) }; return { demandes, remove } }
