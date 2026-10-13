<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import LayoutReparateur from '../../layouts/LayoutReparateur.vue'
import CarteDemandeEntrante from '../../components/reparateur/CarteDemandeEntrante.vue'
import { accepterDemande, chargerDemandes, refuserDemande } from '../../services/serviceDemandes'

const demandes = ref([])
const selection = ref(null)
const chargement = ref(true)
const traitement = ref(false)
const erreur = ref('')
let actualisationInterval = null
let actualisationEnCours = false
const titreStatut = { EN_ATTENTE: 'Nouveau', ACCEPTEE: 'Acceptée', REFUSEE: 'Refusée', ANNULEE: 'Annulée' }
const couleurStatut = { EN_ATTENTE: 'jaune', ACCEPTEE: 'bleu', REFUSEE: 'rouge', ANNULEE: 'rouge' }
const mapper = demande => {
  const client = demande.client_detail || {}
  const lieu = demande.localisation_detail || {}
  return {
    id: demande.id,
    client: client.nom || 'Client',
    photo: client.photo_profil || '',
    telephone: client.telephone || 'Non renseigné',
    adresse: [lieu.adresse, lieu.ville].filter(Boolean).join(', ') || 'Non renseignée',
    zone: [lieu.ville, lieu.quartier || lieu.nom].filter(Boolean).join(', ') || 'Zone non renseignée',
    modeIntervention: demande.mode_intervention === 'ATELIER' ? 'À l’atelier' : 'À domicile',
    adresseIntervention: demande.adresse_intervention || '',
    appareil: demande.appareil || demande.specialite_detail?.nom || 'Réparation',
    panne: demande.specialite_detail?.nom || '',
    modele: demande.appareil || 'Non renseigné',
    description: demande.description_probleme,
    photos: (demande.pieces_jointes || []).filter(piece => piece.fichier).map(piece => ({ id: piece.id, nom: piece.nom_fichier, url: piece.fichier })),
    statut: titreStatut[demande.statut] || demande.statut,
    couleur: couleurStatut[demande.statut] || 'jaune',
    temps: new Date(demande.date_creation).toLocaleString('fr-FR'),
  }
}
const demandesEnAttente = computed(() => demandes.value.filter(demande => demande.statut === 'Nouveau').length)
const charger = async ({ silencieux = false } = {}) => {
  if (actualisationEnCours) return
  actualisationEnCours = true
  if (!silencieux) chargement.value = true
  if (!silencieux) erreur.value = ''
  try {
    const selectionId = selection.value?.id
    const liste = (await chargerDemandes({ contexte: 'reparateur' })).map(mapper)
    demandes.value = liste
    selection.value = liste.find(demande => demande.id === selectionId) || liste[0] || null
  } catch (error) {
    if (!silencieux || !demandes.value.length) erreur.value = error.message
  } finally {
    actualisationEnCours = false
    chargement.value = false
  }
}
const traiter = async (action) => {
  if (!selection.value || traitement.value) return
  traitement.value = true
  erreur.value = ''
  try {
    const resultat = action === 'accepter' ? await accepterDemande(selection.value.id) : await refuserDemande(selection.value.id)
    const miseAJour = mapper(resultat)
    demandes.value = demandes.value.map(demande => demande.id === miseAJour.id ? miseAJour : demande)
    selection.value = miseAJour
  } catch (error) { erreur.value = error.message } finally { traitement.value = false }
}
const actualiserSiVisible = () => {
  if (document.visibilityState === 'visible') charger({ silencieux: true })
}

onMounted(() => {
  charger()
  actualisationInterval = window.setInterval(actualiserSiVisible, 5000)
  document.addEventListener('visibilitychange', actualiserSiVisible)
})

onBeforeUnmount(() => {
  if (actualisationInterval) window.clearInterval(actualisationInterval)
  document.removeEventListener('visibilitychange', actualiserSiVisible)
})
</script>

<template>
  <LayoutReparateur>
    <section class="demandes-page">
      <section class="liste-demandes panneau">
        <header><h1>Demandes ({{ demandesEnAttente }})</h1><button class="filtre" @click="charger">Actualiser</button></header>
        <p v-if="chargement">Chargement des demandes…</p><p v-else-if="erreur">{{ erreur }}</p>
        <div class="liste-scroll">
          <CarteDemandeEntrante v-for="demande in demandes" :key="demande.id" :demande="demande" :selectionnee="selection?.id === demande.id" @selectionner="selection = $event" />
        </div>
      </section>

      <section v-if="selection" class="detail-demande panneau">
        <h1>Détail de la demande <em>#{{ selection.id }}</em></h1>
        <article><h2><span><AppIcon name="user" :size="16"/></span> Client & localisation</h2><div class="client-lieu"><div><b><AppIcon name="user" :size="14"/> {{ selection.client }}</b><small><AppIcon name="phone" :size="14"/> {{ selection.telephone }}</small></div><div><b><AppIcon name="pin" :size="14"/> {{ selection.adresse }}</b><small>{{ selection.modeIntervention }}<template v-if="selection.adresseIntervention"> · {{ selection.adresseIntervention }}</template></small></div></div></article>
        <article><h2><span><AppIcon name="smartphone" :size="16"/></span> Appareil & description de la panne</h2><div class="description"><p><b>Appareil :</b>　{{ selection.modele }}</p><p><AppIcon name="message" :size="14"/> "{{ selection.description }}"</p></div></article>
        <article v-if="selection.photos.length" class="photos-demande"><h2><span><AppIcon name="camera" :size="16"/></span> Photos du problème ({{ selection.photos.length }})</h2><div class="pieces"><figure v-for="photo in selection.photos" :key="photo.id"><a :href="photo.url" target="_blank" rel="noopener noreferrer" :aria-label="`Ouvrir la photo ${photo.nom}`"><img :src="photo.url" :alt="photo.nom" loading="lazy"></a><figcaption>{{ photo.nom }}</figcaption></figure></div></article>
      </section>
      <section v-else class="detail-demande panneau"><p>Aucune demande disponible.</p></section>
    </section>
  </LayoutReparateur>
</template>

<style scoped>
.demandes-page{display:grid;grid-template-columns:48% 1fr;gap:22px;width:min(90vw,1460px);max-width:1460px;margin:0 auto;padding:0}.panneau{background:#fff;border:1px solid #dfeee8;border-radius:10px;box-shadow:0 2px 12px rgba(8,127,112,.08)}.liste-demandes{padding:14px}.liste-demandes header{height:42px;display:flex;justify-content:space-between;align-items:center;padding:0 8px 10px;border-bottom:1px solid #e5f1ee}.liste-demandes h1,.detail-demande>h1{margin:0;text-transform:uppercase;font-size:18px;color:#123f45}.filtre{height:36px;min-width:160px;border:1px solid #cfe9e3;border-radius:9px;background:#f8fcfb;padding:0 14px;color:#0c665d;font:600 12px inherit}.liste-scroll{max-height:720px;overflow:hidden;padding:14px 0 5px;width:calc(100% - 90px);margin:0 auto}.detail-demande{padding:14px;color:#123f45}.detail-demande>h1{padding:0 6px 18px}.detail-demande>h1 em{color:#087f70;font-style:normal}.detail-demande article{border-bottom:1px solid #e8f4f1;padding-bottom:14px;margin-bottom:11px}.detail-demande h2{display:flex;align-items:center;gap:13px;height:47px;margin:0;background:linear-gradient(100deg,#eefaf7,#f8fbfa);border-radius:9px;padding:0 13px;text-transform:uppercase;color:#0d665c;font-size:13px}.detail-demande h2 span{display:none}.client-lieu{display:grid;grid-template-columns:1fr 1.3fr;padding:16px 15px 5px;gap:18px}.client-lieu>div+div{border-left:1px solid #dfeee8;padding-left:21px}.client-lieu b,.client-lieu small{display:block;font-size:13px;line-height:1.85}.client-lieu small{color:#446c6e}.description{padding:13px 16px 5px;font-size:13px;line-height:1.5}.description p{margin:5px 0}.pieces{display:flex;gap:29px;padding:12px 17px 2px}.pieces figure{margin:0;width:202px;border:1px solid #dfeee8;border-radius:9px;overflow:hidden;background:#fff;box-shadow:0 3px 12px rgba(8,63,69,.08)}.pieces a{display:block;height:150px;background:#f4f8f7}.pieces img{display:block;width:100%;height:100%;object-fit:cover;transition:transform .2s ease}.pieces a:hover img{transform:scale(1.04)}.pieces figcaption{overflow:hidden;padding:8px 10px;color:#557276;font-size:11px;text-overflow:ellipsis;white-space:nowrap}
@media(max-width:900px){.pieces{flex-wrap:wrap;gap:12px}.pieces figure{width:min(202px,calc(50% - 6px))}}

/* Utiliser uniquement la largeur disponible après la barre latérale. */
.demandes-page{box-sizing:border-box;width:100%;max-width:1600px;grid-template-columns:minmax(270px,.72fr) minmax(0,1.5fr);gap:20px}
.liste-demandes,.detail-demande{box-sizing:border-box;min-width:0;width:100%}
.liste-scroll{box-sizing:border-box;width:100%;padding-right:2px;padding-left:2px}
.client-lieu{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
.client-lieu>div,.client-lieu b,.client-lieu small,.description{min-width:0;overflow-wrap:anywhere}
.pieces{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr));gap:14px;padding-right:12px;padding-left:12px}
.pieces figure{width:100%;min-width:0;box-sizing:border-box}
.liste-demandes h1,.detail-demande>h1{font-size:16px;letter-spacing:.1px}
@media(max-width:900px){.demandes-page{grid-template-columns:minmax(0,1fr)}.liste-scroll{max-height:460px;overflow-y:auto}.pieces{grid-template-columns:repeat(auto-fit,minmax(min(100%,190px),1fr))}}
</style>
