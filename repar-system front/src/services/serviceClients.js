import { ref } from 'vue'
const photo = (id) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=140&q=85`
const clients = ref([
  {id:'C-001',name:'Mamadou Fall',phone:'+221 77 123 45 67',email:'mamadou.fall@email.sn',address:'Dakar, Plateau',requests:5,status:'Actif',image:photo('photo-1506794778202-cad84cf45f1d')},
  {id:'C-002',name:'Fatou Cissé',phone:'+221 77 890 12 34',email:'fatou.cisse@email.sn',address:'Dakar, Liberté 6',requests:2,status:'Actif',image:photo('photo-1534528741775-53994a69daeb')},
  {id:'C-003',name:'Omar Ndiaye',phone:'+221 76 543 21 09',email:'omar.ndiaye@email.sn',address:'Dakar, Almadies',requests:12,status:'Actif',image:photo('photo-1500648767791-00dcc994a43e')},
  {id:'C-004',name:'Aminata Diallo',phone:'+221 77 654 32 10',email:'aminata.diallo@email.sn',address:'Dakar, Ngor',requests:1,status:'Bloqué',image:photo('photo-1494790108377-be9c29b29330')},
])
export function useClients(){const toggle=client=>client.status=client.status==='Bloqué'?'Actif':'Bloqué';return{clients,toggle}}
