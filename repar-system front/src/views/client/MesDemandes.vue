<template>
  <div class="client">
    <header>
      <RouterLink to="/" class="brand"><i>R</i> ReparSystem</RouterLink>
      <nav>
        <RouterLink to="/">Accueil</RouterLink>
        <RouterLink to="/reparateurs">Trouver un réparateur</RouterLink>
        <RouterLink to="/diagnostic">Faire un diagnostic</RouterLink>
        <RouterLink to="/devenir-reparateur">Devenir réparateur</RouterLink>
        <a>À propos</a>
      </nav>
      <aside><EnteteClient /></aside>
    </header>

    <section class="hero">
      <span>MON COMPTE</span>
      <h1>Mes <em>demandes</em></h1>
      <p>Suivez l'évolution de vos demandes de réparation et restez informé en temps réel.</p>
    </section>

    <main>
      <div class="filters" aria-label="Filtrer les demandes par statut">
        <button v-for="item in filters" :key="item.key" type="button" :class="{ selected: filter === item.key }" @click="filter = item.key">
          {{ item.icon }}　{{ item.label }}
        </button>
      </div>

      <p v-if="loading" class="request-message" role="status">Chargement de vos demandes…</p>
      <div v-else-if="error" class="request-message request-error" role="alert">
        <p>{{ error }}</p>
        <button type="button" @click="charger">Réessayer</button>
      </div>
      <p v-else-if="!requests.length" class="request-message">Vous n’avez pas encore envoyé de demande de réparation.</p>
      <p v-else-if="!visible.length" class="request-message">Aucune demande pour ce statut.</p>

      <template v-else>
        <article v-for="item in visible" :key="item.id" class="request">
          <div class="device-thumbnail" :aria-label="item.device"><span>{{ item.deviceIcon }}</span></div>
          <section class="request-summary">
            <h2>{{ item.device }}</h2>
            <p>{{ item.issue }}</p>
            <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
            <i v-if="item.description">“{{ item.description }}”</i>
            <small>▣　 Demande #{{ item.id }}</small>
          </section>
          <section class="pro">
            <img v-if="item.proImage" :src="item.proImage" :alt="item.pro">
            <span v-else class="pro-avatar" aria-hidden="true">{{ item.proInitials }}</span>
            <b>{{ item.pro }}</b>
            <small>Réparateur</small>
            <p>●　 {{ item.zone }}</p>
            <p>▣　 {{ item.date }}</p>
          </section>
          <section class="state">
            <mark :class="item.key">{{ item.icon }}　{{ item.status }}</mark>
            <button type="button" @click="ouvrirDetails(item)">⊙　 Voir le détail</button>
            <button v-if="item.statut === 'ACCEPTEE' && !avisParDemande[item.id]" class="leave-review" type="button" @click="ouvrirDetails(item)">★　Laisser un avis</button>
          </section>
          <strong class="request-arrow" aria-hidden="true">›</strong>
        </article>
      </template>
    </main>

    <div v-if="selectedRequest" class="detail-overlay" @click.self="selectedRequest = null">
      <section class="detail-modal" role="dialog" aria-modal="true" :aria-labelledby="`detail-title-${selectedRequest.id}`">
        <button class="detail-close" type="button" aria-label="Fermer" @click="selectedRequest = null">×</button>
        <span class="detail-eyebrow">DÉTAIL DE LA DEMANDE #{{ selectedRequest.id }}</span>
        <h2 :id="`detail-title-${selectedRequest.id}`">{{ selectedRequest.device }}</h2>
        <p><strong>Statut :</strong> {{ selectedRequest.status }}</p>
        <p><strong>Spécialité :</strong> {{ selectedRequest.issue }}</p>
        <p><strong>Description :</strong> {{ selectedRequest.description || 'Aucune description fournie.' }}</p>
        <p><strong>Réparateur :</strong> {{ selectedRequest.pro }}</p>
        <p><strong>Localisation :</strong> {{ selectedRequest.zone }}</p>
        <p><strong>Mode d’intervention :</strong> {{ selectedRequest.mode }}</p>
        <p v-if="selectedRequest.address"><strong>Adresse / repère :</strong> {{ selectedRequest.address }}</p>
        <p><strong>Créée le :</strong> {{ selectedRequest.date }}</p>
        <section v-if="selectedRequest.statut === 'ACCEPTEE'" class="review-section">
          <h3>Votre avis sur {{ selectedRequest.pro }}</h3>
          <p v-if="avisParDemande[selectedRequest.id]" class="review-confirmation">Merci, votre avis de {{ avisParDemande[selectedRequest.id].note }}/5 a été envoyé au réparateur.</p>
          <form v-else class="review-form" @submit.prevent="envoyerAvis">
            <label>Votre note
              <select v-model.number="formAvis.note" required>
                <option :value="5">★★★★★ — Excellent</option>
                <option :value="4">★★★★ — Très bien</option>
                <option :value="3">★★★ — Bien</option>
                <option :value="2">★★ — Moyen</option>
                <option :value="1">★ — À améliorer</option>
              </select>
            </label>
            <label>Votre commentaire (facultatif)
              <textarea v-model="formAvis.commentaire" maxlength="2000" rows="4" placeholder="Racontez votre expérience avec ce réparateur…"></textarea>
            </label>
            <p v-if="erreurAvis" class="review-error" role="alert">{{ erreurAvis }}</p>
            <button type="submit" :disabled="envoiAvis">{{ envoiAvis ? 'Envoi…' : 'Envoyer mon avis' }}</button>
          </form>
        </section>
      </section>
    </div>

    <footer>
      <b><i>R</i> ReparSystem</b>
      <span>Services<br><small>Smartphone & Tablette<br>Ordinateur<br>Électroménager</small></span>
      <span>L'entreprise<br><small>À propos<br>Comment ça marche ?<br>Contact</small></span>
      <span>Support<br><small>Centre d'aide<br>Contactez-nous<br>Conditions</small></span>
    </footer>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import EnteteClient from '../../components/client/EnteteClient.vue'
import { chargerDemandes } from '../../services/serviceDemandes'
import { chargerAvis, creerAvis } from '../../services/serviceAvis'

const filter = ref('all')
const requests = ref([])
const loading = ref(true)
const error = ref('')
const selectedRequest = ref(null)
const reviews = ref([])
const formAvis = ref({ note: 5, commentaire: '' })
const envoiAvis = ref(false)
const erreurAvis = ref('')
let actualisationInterval = null
let actualisationEnCours = false
let actualisationAvisEnCours = false

const statusDefinitions = [
  { key: 'waiting', value: 'EN_ATTENTE', label: 'En attente', icon: '●' },
  { key: 'accepted', value: 'ACCEPTEE', label: 'Acceptées', icon: '⬟' },
  { key: 'refused', value: 'REFUSEE', label: 'Refusées', icon: '×' },
  { key: 'cancelled', value: 'ANNULEE', label: 'Annulées', icon: '×' },
]

const filters = computed(() => [
  { key: 'all', label: `Toutes (${requests.value.length})`, icon: '☷' },
  ...statusDefinitions.map((status) => ({
    ...status,
    label: `${status.label} (${requests.value.filter(request => request.statut === status.value).length})`,
  })),
])

const normalizeRequest = (request) => {
  const location = request.localisation_detail || {}
  const repairer = request.reparateur_detail || null
  const status = statusDefinitions.find(item => item.value === request.statut)
  const device = request.appareil || 'Réparation'
  const specialization = request.specialite_detail?.nom || 'Réparation générale'
  const mode = request.mode_intervention === 'ATELIER' ? 'À l’atelier du réparateur' : 'À domicile'
  const createdAt = request.date_creation ? new Date(request.date_creation) : null
  const date = createdAt && !Number.isNaN(createdAt.getTime())
    ? new Intl.DateTimeFormat('fr-FR', { dateStyle: 'long', timeStyle: 'short' }).format(createdAt)
    : 'Date indisponible'
  const repairerName = repairer?.nom || 'En attente d’un réparateur'

  return {
    ...request,
    device,
    deviceIcon: /télé|tv/i.test(device) ? '📺' : /ordinateur|pc|portable/i.test(device) ? '💻' : /lave|électroménager/i.test(device) ? '⚙️' : /smartphone|téléphone|mobile|tablette/i.test(device) ? '📱' : '🔧',
    issue: specialization,
    tags: [specialization, mode],
    description: request.description_probleme || '',
    pro: repairerName,
    proImage: repairer?.photo_profil || '',
    proInitials: repairer ? repairerName.split(/\s+/).map(part => part[0]).slice(0, 2).join('').toUpperCase() : '…',
    zone: [location.quartier, location.ville].filter(Boolean).join(', ') || location.adresse || 'Zone non renseignée',
    date,
    mode,
    address: request.adresse_intervention || '',
    status: status?.label || request.statut || 'Statut inconnu',
    key: status?.key || 'waiting',
    icon: status?.icon || '●',
  }
}

const visible = computed(() => {
  if (filter.value === 'all') return requests.value
  const status = statusDefinitions.find(item => item.key === filter.value)
  return status ? requests.value.filter(request => request.statut === status.value) : requests.value
})

const avisParDemande = computed(() => Object.fromEntries(reviews.value.map(avis => [avis.demande, avis])))

const rafraichirAvis = async () => {
  if (actualisationAvisEnCours) return
  actualisationAvisEnCours = true
  try { reviews.value = await chargerAvis() } catch (_) { /* Les demandes restent consultables si les avis sont momentanément indisponibles. */ } finally { actualisationAvisEnCours = false }
}

const ouvrirDetails = (demande) => {
  selectedRequest.value = demande
  erreurAvis.value = ''
  formAvis.value = { note: 5, commentaire: '' }
}

const envoyerAvis = async () => {
  if (!selectedRequest.value || envoiAvis.value) return
  envoiAvis.value = true
  erreurAvis.value = ''
  try {
    const avis = await creerAvis({
      demande: selectedRequest.value.id,
      note: formAvis.value.note,
      commentaire: formAvis.value.commentaire.trim(),
    })
    reviews.value = [avis, ...reviews.value]
  } catch (error) {
    erreurAvis.value = error.message
  } finally {
    envoiAvis.value = false
  }
}

const charger = async ({ silencieux = false } = {}) => {
  if (actualisationEnCours) return
  actualisationEnCours = true
  if (!silencieux) loading.value = true
  if (!silencieux) error.value = ''
  try {
    const demandes = (await chargerDemandes()).map(normalizeRequest)
    requests.value = demandes
    if (selectedRequest.value) {
      selectedRequest.value = demandes.find(item => item.id === selectedRequest.value.id) || null
    }
  } catch (requestError) {
    if (!silencieux || !requests.value.length) error.value = requestError.message
  } finally {
    actualisationEnCours = false
    loading.value = false
  }
}

const actualiserSiVisible = () => {
  if (document.visibilityState === 'visible') charger({ silencieux: true })
}

onMounted(() => {
  charger()
  rafraichirAvis()
  actualisationInterval = window.setInterval(() => {
    actualiserSiVisible()
    if (document.visibilityState === 'visible') rafraichirAvis()
  }, 5000)
  document.addEventListener('visibilitychange', actualiserSiVisible)
})

onBeforeUnmount(() => {
  if (actualisationInterval) window.clearInterval(actualisationInterval)
  document.removeEventListener('visibilitychange', actualiserSiVisible)
})
</script>
<style scoped>
/* Styles de base restaurés pour l’en-tête, la bannière et le pied de page. */
.client{min-height:100vh;background:#f4f8fc;color:#17345f;font-family:Inter,Arial,sans-serif}
.client *{box-sizing:border-box}
.client header{height:72px;display:flex;align-items:center;gap:clamp(18px,3vw,48px);padding:0 max(5%,32px);background:#fff;border-bottom:1px solid #e5edf5}
.client .brand{display:flex;align-items:center;gap:9px;flex:none;color:#12376c;font-size:17px;font-weight:800;text-decoration:none;white-space:nowrap}
.client .brand i,.client footer i{display:inline-grid;place-items:center;width:32px;height:32px;border-radius:8px;background:#087f70;color:#fff;font-style:normal}
.client nav{display:flex;align-items:center;justify-content:center;gap:clamp(14px,2vw,30px);flex:1}
.client nav a{color:#405878;font-size:12px;font-weight:650;text-decoration:none;white-space:nowrap}
.client nav a:hover{color:#087f70}
.client header aside{display:flex;align-items:center;flex:none}
.client .hero{height:auto;min-height:215px;padding:36px max(6%,40px);color:#fff;background:linear-gradient(100deg,rgba(5,29,66,.96),rgba(8,57,101,.76)),url('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1600&q=85') center 45%/cover}
.client .hero>span{display:inline-block;padding:7px 13px;border-radius:20px;background:#087f70;color:#fff;font-size:10px;font-weight:800;letter-spacing:.8px}
.client .hero h1{margin:14px 0 8px;color:#fff;font-size:clamp(30px,4vw,42px);line-height:1.12}
.client .hero em{color:#48c8ad;font-style:normal}
.client .hero p{max-width:560px;margin:0;color:#d6e4f1;font-size:14px;line-height:1.6}
.client main{display:block;width:calc(100% - 64px);max-width:1450px;margin:28px auto 40px;padding:0;background:transparent}
.client .filters{display:flex;gap:12px;overflow-x:auto;padding:11px;margin-bottom:14px;border:1px solid #dce8f2;border-radius:12px;background:#fff}
.client .filters button{flex:1;min-width:125px;height:44px;border:1px solid #d9e6f4;border-radius:10px;background:#fff;color:#164a86;font-size:12px;font-weight:700;white-space:nowrap;cursor:pointer;transition:background .18s,border-color .18s,color .18s}
.client .filters button:hover{border-color:#8fcfc2;background:#f3fbf9}
.client .filters .selected{border-color:#087f70;background:#087f70;color:#fff}
.client .request{display:grid;grid-template-columns:116px minmax(280px,1.45fr) minmax(235px,1.15fr) minmax(175px,.8fr) 38px;gap:22px;align-items:center;min-height:172px;margin-top:14px;padding:18px 24px;border:1px solid #d6e5f4;border-radius:12px;background:#fff;box-shadow:0 5px 18px rgba(22,67,112,.045)}
.client .device-thumbnail{display:grid;place-items:center;width:108px;height:110px;border:1px solid #e2edf5;border-radius:10px;background:linear-gradient(145deg,#eaf5f4,#eaf0fa);font-size:38px}
.client .request-summary{min-width:0}
.client .request h2{margin:0;color:#12376c;font-size:16px;line-height:1.35}
.client .request p{margin:7px 0;color:#496b9e;font-size:12px;line-height:1.45}
.client .request-summary>span{display:inline-block;margin:4px 5px 3px 0;padding:6px 10px;border-radius:8px;background:#e8f5f2;color:#087f70;font-size:10px;font-weight:600}
.client .request-summary>i{display:block;margin:7px 0;color:#526f9a;font-size:12px;line-height:1.5}
.client .request small{display:block;color:#5576a7;font-size:11px;line-height:1.5}
.client .request .pro{display:grid;grid-template-columns:48px minmax(0,1fr);grid-template-rows:auto auto auto auto;gap:3px 12px;align-items:center;min-width:0;padding-left:20px;border-left:1px solid #dce8f5}
.client .request .pro>img,.client .request .pro-avatar{grid-column:1;grid-row:1/span 2;width:48px;height:48px;border-radius:50%;object-fit:cover}
.client .request .pro-avatar{display:grid;place-items:center;background:#e4efff;color:#174b91;font-size:13px;font-weight:800}
.client .request .pro>b{grid-column:2;grid-row:1;overflow:hidden;color:#12376c;font-size:13px;text-overflow:ellipsis;white-space:nowrap}
.client .request .pro>small{grid-column:2;grid-row:2}
.client .request .pro>p{grid-column:1/-1;margin:5px 0 0;overflow-wrap:anywhere;font-size:12px}
.client .request .state{display:grid;justify-items:start;gap:14px;min-width:0}
.client .request .state mark{display:inline-block;padding:9px 13px;border:0;border-radius:24px;background:#fff0d7;color:#a86700;font-size:11px;white-space:nowrap}
.client .request .state mark.accepted{background:#e2f0ff;color:#087f70}
.client .request .state mark.done{background:#dcf7eb;color:#12825f}
.client .request .state mark.progress{background:#e5f0ff;color:#2363a8}
.client .request .state mark.refused{background:#fde7e9;color:#a52e3a}
.client .request .state mark.cancelled{background:#eef0f3;color:#5f6e80}
.client .request .state button{width:100%;min-height:42px;border:1px solid #087f70;border-radius:9px;background:#fff;color:#087f70;font-size:11px;font-weight:700;cursor:pointer}
.client .request .state button:hover{background:#eef9f6}
.client .request-arrow{color:#164a86;font-size:22px;text-align:center}
.client .request-message{margin:18px 0;padding:25px;border:1px solid #d6e8fb;border-radius:12px;background:#fff;color:#496b9e;font-size:14px;line-height:1.6;text-align:center}
.client .request-error{border-color:#f1c7cc;background:#fff7f7;color:#a52e3a}
.client .request-error button{padding:9px 13px;border:0;border-radius:7px;background:#087f70;color:#fff;cursor:pointer}
.client .detail-overlay{position:fixed;z-index:50;inset:0;display:grid;place-items:center;padding:20px;background:#0b1e38a8}
.client .detail-modal{position:relative;width:min(100%,580px);max-height:min(85vh,760px);overflow:auto;padding:32px;border:1px solid #dce8f4;border-radius:16px;background:#fff;box-shadow:0 24px 70px #071a2b55;color:#23466f}
.client .detail-close{position:absolute;top:13px;right:16px;width:34px;height:34px;border:0;border-radius:50%;background:#eef4fa;color:#345b83;font-size:23px;cursor:pointer}
.client .detail-eyebrow{color:#087f70;font-size:10px;font-weight:800;letter-spacing:1px}
.client .detail-modal h2{margin:11px 40px 22px 0;color:#12376c;font-size:23px}
.client .detail-modal p{margin:12px 0;color:#526e91;font-size:13px;line-height:1.6;overflow-wrap:anywhere}
.client .detail-modal p strong{color:#23466f}
.client .review-section{margin-top:24px;padding:20px;border:1px solid #d8e9e8;border-radius:12px;background:#f7fcfb}
.client .review-section h3{margin:0 0 15px;color:#12376c;font-size:17px}
.client .review-form{display:grid;gap:14px}
.client .review-form label{display:grid;gap:7px;color:#23466f;font-size:12px;font-weight:700}
.client .review-form select,.client .review-form textarea{width:100%;border:1px solid #d4e2ee;border-radius:8px;background:#fff;color:#23466f;font:inherit;padding:11px}
.client .review-form textarea{resize:vertical;line-height:1.5}
.client .review-form>button{justify-self:start;min-height:42px;padding:0 18px;border:0;border-radius:8px;background:#087f70;color:#fff;font-size:12px;font-weight:700;cursor:pointer}
.client .review-form>button:disabled{opacity:.6;cursor:wait}
.client .review-error{margin:0!important;color:#a52e3a!important}
.client .review-confirmation{margin:0!important;padding:13px;border-radius:8px;background:#e8f7ef;color:#117850!important}
.client .request .state .leave-review{border-color:#0aa37f;background:#edf9f6;color:#087f70}
.client .request .state .leave-review:hover{background:#dff4ed}
.client footer{display:grid;grid-template-columns:1.4fr repeat(3,1fr);gap:35px;padding:38px max(6%,40px);background:#08172c;color:#fff;font-size:13px;font-weight:700}
.client footer>b{display:flex;align-items:center;font-size:17px}
.client footer>span{line-height:1.8}
.client footer small{color:#bfcede;font-size:11px;font-weight:400}
@media(max-width:1050px){.client main{width:calc(100% - 40px)}.client .request{grid-template-columns:96px minmax(190px,1.3fr) minmax(175px,1fr) 150px 28px;gap:14px;padding:16px}.client .device-thumbnail{width:90px;height:96px}.client .request .pro{padding-left:14px}}
@media(max-width:800px){.client header{height:auto;min-height:64px;padding:10px 20px;gap:16px}.client nav{justify-content:flex-end;gap:12px;flex-wrap:wrap}.client nav a{font-size:10px}.client .hero{min-height:190px;padding:30px 24px}.client main{width:auto;margin:18px 16px 30px}.client footer{grid-template-columns:1fr 1fr;gap:24px}}
@media(max-width:720px){.client header{flex-wrap:wrap}.client nav{order:3;flex-basis:100%;justify-content:flex-start;overflow-x:auto;flex-wrap:nowrap;padding:4px 0}.client .request{grid-template-columns:76px minmax(0,1fr) 30px;gap:12px;padding:14px;min-height:0}.client .device-thumbnail{grid-column:1;grid-row:1;width:76px;height:82px;font-size:30px}.client .request-summary{grid-column:2;grid-row:1}.client .request .pro{grid-column:1/3;grid-row:2;grid-template-columns:42px minmax(0,1fr);padding:12px 0 0;border-top:1px solid #e4edf7;border-left:0}.client .request .pro>img,.client .request .pro-avatar{width:42px;height:42px}.client .request .state{grid-column:1/3;grid-row:3;display:flex;align-items:center;gap:14px}.client .request .state button{flex:1;width:auto;margin:0}.client .request-arrow{grid-column:3;grid-row:1}.client .filters{gap:8px}.client .filters button{min-width:118px}}
@media(max-width:480px){.client .hero p{font-size:12px}.client .request{gap:9px;padding:12px}.client .request h2{font-size:14px}.client .request p{font-size:11px}.client .request-summary>i{font-size:11px}.client .request .state{align-items:stretch;flex-direction:column;gap:8px}.client .request .state button{min-height:38px}}
/* Cartes plus larges et informations plus confortables à lire. */
main{width:calc(100% - 64px);max-width:1450px;margin:28px auto 40px}
.filters{gap:12px;padding:11px;margin-bottom:14px}
.filters button{height:44px;font-size:12px;font-weight:700}
.request{grid-template-columns:116px minmax(280px,1.45fr) minmax(235px,1.15fr) minmax(175px,.8fr) 38px;gap:22px;min-height:172px;margin-top:14px;padding:18px 24px;border-radius:12px;box-shadow:0 5px 18px rgba(22,67,112,.045)}
.request>img{width:108px;height:110px;border-radius:10px}
.request h2{font-size:16px;line-height:1.35;color:#12376c}
.request p{margin:7px 0;color:#496b9e;font-size:12px;line-height:1.45}
.request section>span{margin:4px 5px 3px 0;padding:6px 10px;font-size:10px}
.request section>i{display:block;margin:7px 0;color:#526f9a;font-size:12px;line-height:1.5}
.request small{font-size:11px;line-height:1.5;color:#5576a7}
.request .pro{padding-left:20px}
.request .pro img{width:48px;height:48px}
.request .pro b{font-size:13px;color:#12376c}
.request .pro p{font-size:12px}
.request .state mark{padding:9px 13px;font-size:11px}
.request .state button{min-height:42px;font-size:11px;font-weight:700}
.request>strong{font-size:18px}
.device-thumbnail{display:grid;place-items:center;width:108px;height:110px;border-radius:10px;background:linear-gradient(145deg,#eaf5f4,#eaf0fa);font-size:38px}
.request .pro-avatar{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:#e4efff;color:#174b91;font-size:13px;font-weight:800}
.request-error{border-color:#f1c7cc;background:#fff7f7;color:#a52e3a}
.request-error button{padding:9px 13px;border-radius:7px;background:#087f70;color:#fff}
.detail-overlay{position:fixed;z-index:50;inset:0;display:grid;place-items:center;padding:20px;background:#0b1e38a8}
.detail-modal{position:relative;width:min(100%,580px);max-height:min(85vh,760px);overflow:auto;padding:32px;border:1px solid #dce8f4;border-radius:16px;background:#fff;box-shadow:0 24px 70px #071a2b55;color:#23466f}
.detail-close{position:absolute;top:13px;right:16px;width:34px;height:34px;border:0;border-radius:50%;background:#eef4fa;color:#345b83;font-size:23px;cursor:pointer}
.detail-eyebrow{color:#087f70;font-size:10px;font-weight:800;letter-spacing:1px}
.detail-modal h2{margin:11px 40px 22px 0;color:#12376c;font-size:23px}
.detail-modal p{margin:12px 0;color:#526e91;font-size:13px;line-height:1.6;overflow-wrap:anywhere}
.detail-modal p strong{color:#23466f}
.request-message{margin:18px 0;padding:25px;border:1px solid #d6e8fb;border-radius:12px;background:#fff;color:#496b9e;font-size:14px;line-height:1.6;text-align:center}
.request-message p{margin:0 0 12px}
.request .refused{background:#fde7e9;color:#a52e3a}
.request .cancelled{background:#eef0f3;color:#5f6e80}
@media(max-width:1050px){main{width:calc(100% - 40px)}.request{grid-template-columns:96px minmax(190px,1.3fr) minmax(175px,1fr) 150px 28px;gap:14px;padding:16px}.request>img{width:90px;height:96px}.request .pro{padding-left:14px}}
@media(max-width:720px){main{width:auto;margin:18px 16px 30px}.request{grid-template-columns:76px minmax(0,1fr) 30px;gap:12px;padding:14px;min-height:0}.request>img{grid-row:1;width:76px;height:82px}.request>section:first-of-type{grid-column:2;grid-row:1}.request .pro{grid-column:1/3;grid-row:2;border-top:1px solid #e4edf7;border-left:0;padding:12px 0 0}.request .state{grid-column:1/3;grid-row:3;display:flex;align-items:center;gap:14px}.request .state button{flex:1;margin:0}.request>strong{grid-column:3;grid-row:1}}
</style>
