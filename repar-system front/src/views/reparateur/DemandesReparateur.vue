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
    telephone: client.telephone || 'Non renseigné',
    adresse: [lieu.adresse, lieu.ville].filter(Boolean).join(', ') || 'Non renseignée',
    zone: [lieu.ville, lieu.quartier || lieu.nom].filter(Boolean).join(', ') || 'Zone non renseignée',
    modeIntervention: demande.mode_intervention === 'ATELIER' ? 'À l’atelier' : 'À domicile',
    adresseIntervention: demande.adresse_intervention || '',
    appareil: demande.appareil || demande.specialite_detail?.nom || 'Réparation',
    panne: demande.specialite_detail?.nom || 'Demande de réparation',
    modele: demande.appareil || 'Non renseigné',
    description: demande.description_probleme,
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
        <header><h1>Demandes entrantes ({{ demandesEnAttente }})</h1><button class="filtre" @click="charger">Actualiser</button></header>
        <p v-if="chargement">Chargement des demandes…</p><p v-else-if="erreur">{{ erreur }}</p>
        <div class="liste-scroll">
          <CarteDemandeEntrante v-for="demande in demandes" :key="demande.id" :demande="demande" :selectionnee="selection?.id === demande.id" @selectionner="selection = $event" />
        </div>
      </section>

      <section v-if="selection" class="detail-demande panneau">
        <h1>Détail de la demande <em>#{{ selection.id }}</em></h1>
        <article><h2><span><AppIcon name="user" :size="16"/></span> Client & localisation</h2><div class="client-lieu"><div><b><AppIcon name="user" :size="14"/> {{ selection.client }}</b><small><AppIcon name="phone" :size="14"/> {{ selection.telephone }}</small></div><div><b><AppIcon name="pin" :size="14"/> {{ selection.adresse }}</b><small>{{ selection.modeIntervention }}<template v-if="selection.adresseIntervention"> · {{ selection.adresseIntervention }}</template></small></div></div></article>
        <article><h2><span><AppIcon name="smartphone" :size="16"/></span> Appareil & description de la panne</h2><div class="description"><p><b>Appareil :</b>　{{ selection.modele }}</p><p><AppIcon name="message" :size="14"/> "{{ selection.description }}"</p></div></article>
        <article><h2><span><AppIcon name="folder" :size="16"/></span> Pièces jointes envoyées par le client</h2><p class="description">Aucune pièce jointe n’est disponible pour cette demande.</p></article>

        <footer class="actions-demande">
          <h2>ϟ　 Action rapide <small>(traitement en 1 clic)</small></h2>
          <div class="actions-boutons">
            <button class="refuser" :disabled="traitement || selection.statut !== 'Nouveau'" @click="traiter('refuser')"><AppIcon name="close" :size="15"/> Refuser la demande</button>
            <button class="accepter" :disabled="traitement || selection.statut !== 'Nouveau'" @click="traiter('accepter')"><AppIcon name="check" :size="15"/> Accepter l'intervention</button>
          </div>
        </footer>
      </section>
      <section v-else class="detail-demande panneau"><p>Aucune demande disponible.</p></section>
    </section>
  </LayoutReparateur>
</template>

<style scoped>
.demandes-page{display:grid;grid-template-columns:46% 1fr;gap:18px;max-width:1334px;margin:auto}.panneau{background:#fff;border:1px solid #e1eaf6;border-radius:10px;box-shadow:0 2px 12px #1647820d}.liste-demandes{padding:16px}.liste-demandes header{height:47px;display:flex;justify-content:space-between;align-items:center;padding:0 9px 12px;border-bottom:1px solid #e5edf8}.liste-demandes h1,.detail-demande>h1{margin:0;text-transform:uppercase;font-size:18px;color:#0a3477}.filtre{height:40px;min-width:177px;border:1px solid #d4e3f9;border-radius:9px;background:#f8fbff;padding:0 15px;color:#244b86;font:600 13px inherit}.liste-scroll{max-height:681px;overflow:hidden;padding:16px 0 6px}.detail-demande{padding:16px 19px 14px;color:#17447f}.detail-demande>h1{padding:5px 6px 22px}.detail-demande>h1 em{color:#146df1;font-style:normal}.detail-demande article{border-bottom:1px solid #e8eef7;padding-bottom:14px;margin-bottom:11px}.detail-demande h2{display:flex;align-items:center;gap:13px;height:47px;margin:0;background:linear-gradient(100deg,#f0f6ff,#f8fbff);border-radius:9px;padding:0 13px;text-transform:uppercase;color:#0759ca;font-size:13px}.detail-demande h2 span{display:grid;place-items:center;width:38px;height:38px;background:#1375f5;border-radius:50%;color:#fff;font-size:18px}.client-lieu{display:grid;grid-template-columns:1fr 1.3fr;padding:16px 15px 5px;gap:18px}.client-lieu>div+div{border-left:1px solid #dbe7f6;padding-left:21px}.client-lieu b,.client-lieu small{display:block;font-size:13px;line-height:1.85}.client-lieu small{color:#174d96}.description{padding:13px 16px 5px;font-size:13px;line-height:1.5}.description p{margin:5px 0}.pieces{display:flex;gap:29px;padding:12px 17px 2px}.pieces figure{margin:0;width:202px;border:1px solid #dbe7f5;border-radius:6px;overflow:hidden}.ecran{height:106px;background:linear-gradient(135deg,#c79257,#e7c081 38%,#352f2e 39%,#0c111b 70%,#7e7e7d);position:relative}.ecran::after{content:'';position:absolute;inset:12px 28px;background:repeating-linear-gradient(48deg,transparent 0 18px,#d8e3ee88 19px 21px,transparent 22px 36px);transform:rotate(-6deg);border-radius:7px}.actions-demande{margin-top:16px;padding-top:16px;border-top:1px solid #e8eef7}.actions-demande h2{display:flex;align-items:center;gap:10px;margin:0 0 16px;background:linear-gradient(100deg,#eef6ff,#f4faff);padding:12px 16px;border-radius:9px;text-transform:uppercase;font-size:13px;color:#0c4c9d}.actions-demande h2 small{font-size:11px;color:#6d86a9;font-weight:600}.actions-boutons{display:flex;justify-content:flex-end;gap:12px;flex-wrap:wrap}.actions-boutons button{height:40px;padding:0 18px;border-radius:8px;border:1px solid transparent;font:700 12px/1 inherit;cursor:pointer;transition:transform .15s ease, box-shadow .15s ease}.actions-boutons button:hover:not(:disabled){transform:translateY(-1px);box-shadow:0 10px 18px rgba(20,92,178,.12)}.actions-boutons .refuser{background:#fff1f3;color:#cd3f59;border-color:#f5c6d2}.actions-boutons .accepter{background:#0d8d7a;color:#fff;border-color:#0d8d7a}.actions-boutons button:disabled{cursor:not-allowed;opacity:.55}.casse-2{background:linear-gradient(145deg,#3a4b60,#0a111b 57%,#b7956a)}.pieces figcaption{padding:10px;color:#255b9c;font-size:10px}footer{background:linear-gradient(100deg,#eef5ff,#f5f9ff);border-radius:8px;margin-top:13px;padding:12px 15px}footer h2{height:auto;background:transparent;padding:0;font-size:13px}footer h2 small{font-size:11px}footer>div{display:grid;grid-template-columns:1fr 1fr;gap:21px;margin-top:13px}footer button{height:46px;border-radius:8px;background:#fff;font-size:12px;font-weight:700}.refuser{border:1px solid #ff5362;color:#f13d4d}.accepter{border:1px solid #08ad78;background:linear-gradient(90deg,#09bc85,#00a36e);color:#fff;box-shadow:0 3px 6px #0eb17b33}@media(max-width:1100px){.demandes-page{grid-template-columns:43% 1fr}.detail-demande{padding:13px}.pieces figure{width:42%}}@media(max-width:850px){.demandes-page{grid-template-columns:1fr}.liste-scroll{max-height:440px}.detail-demande{min-width:0}}@media(max-width:500px){.client-lieu{grid-template-columns:1fr}.client-lieu>div+div{border:0;padding:0}.pieces{gap:8px;padding-left:0;padding-right:0}.pieces figure{width:49%}footer>div{grid-template-columns:1fr}.liste-demandes h1,.detail-demande>h1{font-size:14px}.filtre{min-width:115px}}
</style>
