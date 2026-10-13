<template>
  <div class="overlay" @click.self="$emit('close')">
    <article class="sheet">
      <header>
        <span class="badge"><AppIcon name="users" :size="18"/></span>
        <h2>FICHE CLIENT &amp; HISTORIQUE : {{ clientName }}</h2>
        <button aria-label="Fermer" @click="$emit('close')"><AppIcon name="close" :size="20"/></button>
      </header>

      <main>
        <div class="top">
          <section class="left">
            <div class="identity card">
              <img :src="client.image || defaultImage" :alt="client.name || 'Client'">
              <div>
                <h3>{{ client.name || 'Client' }}</h3>
                <mark><AppIcon name="circle" :size="10" fill="currentColor"/> {{ client.status || 'Actif' }}</mark>
                <small>ID : {{ client.id }}</small>
              </div>
            </div>

            <div class="stats card">
              <p>
                <AppIcon name="clipboard" :size="20"/>
                <span>Total des demandes<b>{{ client.requests || 0 }}</b></span>
              </p>
              <p>
                <AppIcon name="clock" :size="20"/>
                <span>Dernière demande<b>{{ derniereDemande }}</b></span>
              </p>
            </div>
          </section>

          <section class="personal card">
            <h4><AppIcon name="user" :size="15"/> INFORMATIONS PERSONNELLES</h4>
            <dl>
              <dt><AppIcon name="user" :size="14"/> Nom complet :</dt>
              <dd>{{ client.name || 'Non renseigné' }}</dd>
              <dt><AppIcon name="phone" :size="14"/> Téléphone :</dt>
              <dd>{{ client.phone || 'Non renseigné' }}</dd>
              <dt><AppIcon name="mail" :size="14"/> Email :</dt>
              <dd>{{ client.email || 'Non renseigné' }}</dd>
              <dt><AppIcon name="pin" :size="14"/> Adresse :</dt>
              <dd>{{ client.address || 'Adresse non renseignée' }}</dd>
              <dt><AppIcon name="calendar" :size="14"/> Date d'inscription :</dt>
              <dd>{{ dateInscription }}</dd>
            </dl>
          </section>
        </div>

        <section class="history card">
          <h3><AppIcon name="clock" :size="16"/> HISTORIQUE DES DEMANDES DE RÉPARATION ({{ historiqueTotal }} TOTAL)</h3>
          <p v-if="!requests.length">Aucune demande enregistrée pour ce client.</p>
          <div v-else class="table">
            <table>
              <thead>
                <tr>
                  <th>ID DEMANDE</th>
                  <th>DATE</th>
                  <th>APPAREIL / PANNE</th>
                  <th>RÉPARATEUR</th>
                  <th>STATUT</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in requests" :key="request.id">
                  <td><b>#{{ request.id }}</b></td>
                  <td>{{ request.dateLabel }}</td>
                  <td>
                    <div class="device-cell">
                      <AppIcon :name="request.icon" :size="15"/>
                      <div>
                        <b>{{ request.device }}</b>
                        <small>{{ request.issue }}</small>
                      </div>
                    </div>
                  </td>
                  <td><AppIcon name="wrench" :size="14"/> {{ request.pro }}</td>
                  <td>
                    <mark :class="request.statusClass">
                      <AppIcon :name="request.statusIcon" :size="14"/>
                      {{ request.statusLabel }}
                    </mark>
                  </td>
                  <td><button><AppIcon name="info" :size="14"/> Voir détail</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </main>

      <footer>
        <button @click="$emit('block')"><AppIcon name="x-circle" :size="15"/> {{ client.status === 'Bloqué' ? 'Débloquer ce client' : 'Bloquer ce client' }}</button>
      </footer>
    </article>
  </div>
</template>
<script setup>
import { computed } from 'vue'

const props = defineProps({ client: { type: Object, required: true } })
defineEmits(['close', 'block'])

const defaultImage = 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=140&q=80'

const formatDate = (value) => {
  if (!value) return 'Non renseignée'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Non renseignée'
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}

const formatStatus = (status) => {
  switch (status) {
    case 'ACCEPTEE':
      return { label: 'Acceptée', icon: 'check-circle', className: 'done' }
    case 'REFUSEE':
      return { label: 'Refusée', icon: 'x-circle', className: 'refused' }
    case 'ANNULEE':
      return { label: 'Annulée', icon: 'slash', className: 'refused' }
    case 'EN_ATTENTE':
      return { label: 'En attente', icon: 'clock', className: 'pending' }
    default:
      return { label: 'Terminé', icon: 'check-circle', className: 'done' }
  }
}

const clientName = computed(() => (props.client.name || 'CLIENT').toUpperCase())

const requests = computed(() =>
  (props.client.history || []).map((request) => {
    const statut = formatStatus(request.status)
    return {
      ...request,
      dateLabel: formatDate(request.date),
      statusLabel: statut.label,
      statusIcon: statut.icon,
      statusClass: statut.className,
      icon: request.icon || 'wrench',
    }
  })
)

const historiqueTotal = computed(() => requests.value.length || Number(props.client.requests || 0))
const derniereDemande = computed(() => {
  if (!requests.value.length) return '—'
  return requests.value.reduce((dernier, current) => {
    if (!dernier) return current
    return new Date(current.date) > new Date(dernier.date) ? current : dernier
  }).dateLabel
})

const dateInscription = computed(() => formatDate(props.client.dateInscription))

const client = computed(() => ({
  ...props.client,
  image: props.client.image || defaultImage,
  name: props.client.name || 'Client',
  status: props.client.status || 'Actif',
}))
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  background: rgba(17, 34, 43, 0.18);
  padding: 24px;
}

.sheet {
  width: min(1100px, calc(100vw - 48px));
  max-height: calc(100vh - 48px);
  overflow: auto;
  background: #ffffff;
  border: 1px solid #dfeaf7;
  border-radius: 18px;
  box-shadow: 0 22px 52px rgba(7, 39, 53, 0.14);
  color: #174b50;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px 14px;
  border-bottom: 1px solid #e4edf8;
  background: #ffffff;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #edf8f6;
  color: #0d7d71;
}

header h2 {
  flex: 1;
  margin: 0;
  font-size: clamp(1.1rem, 1.7vw, 1.6rem);
  line-height: 1.2;
  color: #163f4d;
  text-transform: uppercase;
}

header button {
  border: none;
  background: transparent;
  color: #0d7d71;
  font-size: 1.8rem;
  cursor: pointer;
}

main {
  padding: 20px;
  background: #ffffff;
}

.top {
  display: grid;
  grid-template-columns: minmax(240px, 320px) minmax(0, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.left,
.personal,
.history {
  background: #ffffff;
}

.card {
  border: 1px solid #e4edf8;
  border-radius: 16px;
  background: #ffffff;
  padding: 16px;
}

.identity {
  display: flex;
  align-items: center;
  gap: 14px;
}

.identity img {
  width: 92px;
  height: 92px;
  border-radius: 18px;
  object-fit: cover;
  border: 1px solid #dfeaf7;
}

.identity h3 {
  margin: 0 0 8px;
  font-size: 1.1rem;
  color: #153f4d;
}

.identity mark,
.personal mark,
.history mark {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 0.7rem;
  font-weight: 700;
}

.identity mark {
  background: #eafaf6;
  color: #0a8d79;
}

.identity small {
  display: block;
  margin-top: 8px;
  color: #58728f;
  font-size: 0.7rem;
}

.stats {
  margin-top: 16px;
}

.stats p {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 10px;
  color: #254f64;
}

.stats span {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 12px;
  font-weight: 600;
}

.stats b {
  color: #0f7e70;
  font-size: 1.05rem;
}

.personal h4,
.history h3 {
  margin: 0 0 16px;
  color: #0d705f;
  font-size: 0.9rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.personal dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px 14px;
  margin: 0;
}

.personal dt,
.personal dd {
  margin: 0;
  color: #1b4d66;
  line-height: 1.7;
}

.personal dt {
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
}

.personal dd {
  color: #2b5d72;
}

.table {
  overflow: auto;
  border: 1px solid #e1ebf7;
  border-radius: 12px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 12px 14px;
  border-bottom: 1px solid #edf3fa;
  text-align: left;
  vertical-align: top;
}

th {
  background: #f3f8fd;
  color: #065d71;
  font-size: 0.7rem;
  text-transform: uppercase;
}

td {
  color: #254f64;
  font-size: 0.82rem;
}

.device-cell {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.device-cell b,
.device-cell small {
  display: block;
}

.device-cell small {
  margin-top: 4px;
  color: #59738f;
}

.done {
  background: #eafaf4;
  color: #0f8d6d;
}

.refused {
  background: #fff0f1;
  color: #d6465d;
}

.pending {
  background: #fff9ea;
  color: #c4841c;
}

footer {
  padding: 18px 20px 22px;
  border-top: 1px solid #e4edf8;
  background: #ffffff;
}

footer button {
  border: 1px solid #ffb5bf;
  background: #fff5f7;
  color: #d13d5d;
  border-radius: 10px;
  padding: 10px 18px;
  font-weight: 700;
  cursor: pointer;
}

@media (max-width: 820px) {
  .top {
    grid-template-columns: 1fr;
  }

  .sheet {
    width: min(100%, calc(100vw - 20px));
  }

  header {
    align-items: flex-start;
  }
}
</style>
