<template>
  <AdministrationLayout>
    <section class="dashboard">
      <header class="title">
        <div><h1>Tableau de bord & statistiques</h1></div>
      </header>
      <p v-if="erreur" class="feedback error" role="alert">{{ erreur }}</p>
      <p v-else-if="chargement" class="feedback">Chargement des statistiques…</p>
      <section class="kpis">
        <article v-for="kpi in kpis" :key="kpi.label" :class="kpi.color"><h2>{{ kpi.label }}</h2><strong>{{ formatter(kpi.value) }}</strong></article>
      </section>
      <section class="panels analytics-grid">
        <article class="panel intervention-card analytics-card">
          <header class="analytics-heading">
            <div>
              <h2>Statistiques d’intervention</h2>
            </div>
          </header>

          <div class="acceptance-content">
            <div class="acceptance-ring" :style="{ '--acceptance': `${acceptancePercent}%` }" role="img" :aria-label="`Taux d’acceptation : ${formatPercent(statistiques.taux_acceptation)}`">
              <div class="acceptance-ring-center">
                <strong>{{ formatPercent(statistiques.taux_acceptation) }}</strong>
                <span>Taux d’acceptation</span>
              </div>
            </div>

            <div class="acceptance-summary">
              <span class="summary-icon"><AppIcon name="check-circle" :size="19" /></span>
              <div>
                <strong>{{ formatter(statistiques.demandes_acceptees) }} demandes acceptées</strong>
                <p>sur {{ formatter(statistiques.demandes_totales) }} demandes reçues</p>
              </div>
            </div>
          </div>

          <div class="acceptance-footer">
            <span><i class="accepted-dot"></i>Acceptées</span>
            <strong>{{ formatter(statistiques.demandes_acceptees) }}</strong>
            <span class="footer-divider"></span>
            <span><i class="other-dot"></i>Autres demandes</span>
            <strong>{{ formatter(demandesNonAcceptees) }}</strong>
          </div>
        </article>
        <article class="panel status-chart-card">
          <header class="status-chart-header">
            <h2>Demandes par statut</h2>
          </header>
          <div v-if="demandesParStatut.length" class="status-chart-content">
            <div class="status-donut-wrap">
              <div class="status-donut" :style="{ background: statusDonutGradient }" role="img" :aria-label="`Répartition de ${formatter(totalDemandesStatut)} demandes par statut`">
                <div class="status-donut-center">
                  <span>Total</span>
                  <strong>{{ formatter(totalDemandesStatut) }}</strong>
                </div>
              </div>
            </div>
            <div class="status-legend">
              <div v-for="item in demandesParStatut" :key="item.key" class="status-legend-row">
                <span class="status-legend-name"><i :style="{ background: item.color }"></i>{{ item.label }}</span>
                <strong>{{ formatter(item.count) }}</strong>
                <small>{{ item.percent }}%</small>
              </div>
            </div>
          </div>
          <div v-else class="status-chart-empty">Aucune demande à afficher pour le moment.</div>
        </article>
      </section>

    </section>
  </AdministrationLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdministrationLayout from '../../components/administrateur/AdministrationLayout.vue'
import { chargerDemandesAdministration } from '../../services/serviceDemandes'

const statistiques = ref({ clients_inscrits: 0, reparateurs_actifs: 0, demandes_totales: 0, zones_couvertes: 0, demandes_acceptees: 0, taux_acceptation: 0, repartition_demandes: [] })
const demandes = ref([])
const chargement = ref(true)
const erreur = ref('')
const formatter = valeur => new Intl.NumberFormat('fr-FR').format(Number(valeur) || 0)
const formatPercent = valeur => `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 }).format(Number(valeur) || 0)}%`
const kpis = computed(() => [
  { label: 'Clients inscrits', value: statistiques.value.clients_inscrits, color: 'blue' },
  { label: 'Réparateurs actifs', value: statistiques.value.reparateurs_actifs, color: 'green' },
  { label: 'Demandes totales', value: statistiques.value.demandes_totales, color: 'purple' },
  { label: 'Zones couvertes', value: statistiques.value.zones_couvertes, color: 'orange' },
])
const acceptancePercent = computed(() => Math.min(100, Math.max(0, Number(statistiques.value.taux_acceptation) || 0)))
const demandesNonAcceptees = computed(() => Math.max(0, Number(statistiques.value.demandes_totales || 0) - Number(statistiques.value.demandes_acceptees || 0)))
const totalDemandesStatut = computed(() => demandes.value.length || Number(statistiques.value.demandes_totales) || 0)
const demandesParStatut = computed(() => {
  if (!totalDemandesStatut.value) return []

  const definitions = [
    { key: 'EN_ATTENTE', label: 'En attente', color: '#73b7f7' },
    { key: 'ACCEPTEE', label: 'Acceptées', color: '#8b7ce8' },
    { key: 'REFUSEE', label: 'Refusées', color: '#f1b45d' },
    { key: 'ANNULEE', label: 'Annulées', color: '#8497ad' },
  ]
  const counts = Object.fromEntries(definitions.map(item => [item.key, 0]))

  demandes.value.forEach(demande => {
    if (counts[demande.statut] !== undefined) counts[demande.statut] += 1
  })

  return definitions.map(item => ({
    ...item,
    count: counts[item.key],
    percent: Math.round(counts[item.key] / totalDemandesStatut.value * 100),
  }))
})
const statusDonutGradient = computed(() => {
  let progression = 0
  const parts = demandesParStatut.value.map(item => {
    const start = progression
    progression += item.count / totalDemandesStatut.value * 100
    return `${item.color} ${start}% ${progression}%`
  })
  return `conic-gradient(${parts.join(', ')})`
})
onMounted(async () => {
  try {
    const resultat = await chargerDemandesAdministration()
    statistiques.value = resultat.statistiques
    demandes.value = resultat.demandes
  }
  catch (error) { erreur.value = error.message }
  finally { chargement.value = false }
})
</script>

<style scoped>
.dashboard{display:grid;gap:20px}.title,.panel{background:#fff;border:1px solid #e1edfa;border-radius:12px}.title{display:flex;align-items:center;gap:14px;padding:16px}.title-icon{width:54px;height:54px;display:grid;place-items:center;background:#e5f4f0;border-radius:12px;color:#087f70;font-size:28px}.title h1{text-transform:uppercase;margin:0;font-size:20px}.title p{margin:7px 0 0;color:#5576ad}.title aside{margin-left:auto;display:flex;gap:10px;padding:10px 14px;background:#f5faff;border:1px solid #ddebfc;border-radius:10px;color:#4471b3;font-size:12px}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.kpis article{min-height:137px;padding:18px;border:1px solid #dceeea;border-radius:10px;background:#fff}.kpis article>span{float:left;width:48px;height:48px;display:grid;place-items:center;border-radius:14px;color:#fff;background:#087f70;font-size:24px;margin-right:14px}.kpis h2{font-size:14px;margin:8px 0}.kpis strong{display:block;font-size:28px;margin-top:18px}.kpis small{display:block;color:#00a879;font-weight:800;margin-top:12px}.kpis small i{font-style:normal;color:#6280b1;margin-left:14px;font-weight:400}.kpis .green>span{background:#29b873}.purple>span{background:#7548e8!important}.orange>span{background:#ff7d2b!important}.panels{display:grid;grid-template-columns:1.1fr .95fr;gap:20px}.panel{padding:16px}.panel h2{margin:0;color:#174b50;font-size:15px;text-transform:uppercase}.distribution-content{display:flex;align-items:center;gap:36px;padding:25px}.donut{width:195px;height:195px;flex:none;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#1976ef 0 45%,#ff8243 45% 80%,#34b879 80%)}.donut b{width:100px;height:100px;background:#fff;border-radius:50%;display:grid;place-content:center;text-align:center;font-size:20px}.donut small,.legend small{display:block;font-weight:400;color:#6682b2;font-size:11px;margin-top:5px}.legend{flex:1}.legend p{display:flex;align-items:center;gap:10px;border-bottom:1px solid #e5effa;padding:13px 0;margin:0}.legend i{width:17px;height:17px;border-radius:50%}.legend span{font-weight:700}.legend b{margin-left:auto;text-align:right}.interventions{margin-top:24px}.interventions>div{border:1px solid #d8ebe8;border-radius:9px;padding:15px;min-height:193px}.interventions span{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#29b873;color:#fff;font-size:21px;margin-right:10px}.interventions b{vertical-align:top;line-height:40px;color:#078157;font-size:13px}.interventions strong{display:block;font-size:31px;margin:25px 0 13px;text-align:center}.interventions small{color:#00a879}.requests header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.requests a{color:#087f70;border:1px solid #cde2ff;border-radius:18px;padding:9px 13px;font-size:12px;font-weight:700}.request-head,.request{display:grid;grid-template-columns:1.1fr 1.2fr 1.1fr 1.1fr 1.4fr 1fr 1.15fr;align-items:center;gap:8px;padding:14px;font-size:12px}.request-head{background:#edf8f5;text-transform:uppercase;color:#416bb0;font-size:10px;font-weight:800}.request{border-bottom:1px solid #e4eef9;color:#345890}.request em,mark{font-style:normal;padding:7px 10px;border-radius:14px;width:max-content;background:#e2efff;color:#087f70}.request mark{background:#fff3dc;color:#e38b00}.request mark.accepted{background:#ddf8ee;color:#00a775}.request button{background:#fff;border:1px solid #8fc1ff;color:#087f70;border-radius:7px;padding:8px;font-size:11px}.none{text-align:center;color:#6580af}@media(max-width:1050px){.kpis{grid-template-columns:repeat(2,1fr)}.panels{grid-template-columns:1fr}.request-head,.request{min-width:900px}.requests{overflow:auto}}@media(max-width:600px){.title{align-items:flex-start}.title h1{font-size:16px}.title aside{display:none}.kpis{grid-template-columns:1fr}.distribution-content{padding:18px;gap:14px}.donut{width:150px;height:150px}.legend p{font-size:12px}}
.kpis article{min-height:112px}.kpis h2{margin:0;color:#5576ad}.kpis strong{margin-top:24px}
.panels > .panel{min-height:390px}
.feedback{margin:0;padding:12px 14px;border-radius:8px;background:#eef8f5;color:#087f70}.feedback.error{background:#fff0f2;color:#c22f45}.empty{padding:52px 20px;text-align:center;color:#6682b2}

/* Analytics cards use the shared ReparSystem brand tokens. */
.panels.analytics-grid {
  grid-template-columns: minmax(0, 1.12fr) minmax(320px, 0.88fr);
  align-items: start;
  gap: 18px;
}

.analytics-card {
  min-height: 318px !important;
  padding: 22px 24px !important;
  border: 1px solid var(--rs-border, #d7e8e3);
  border-radius: 16px !important;
  background: var(--rs-surface, #fff);
  box-shadow: 0 10px 28px rgba(18, 63, 69, 0.06);
}

.analytics-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}

.analytics-heading h2 {
  margin: 0 !important;
  color: var(--rs-ink, #123f45) !important;
  font-size: 17px !important;
  font-weight: 750;
  letter-spacing: -0.025em;
  text-transform: none !important;
}

.eyebrow {
  color: var(--rs-muted, #6d8588);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.heading-icon {
  display: grid;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  place-items: center;
  border-radius: 12px;
  background: var(--rs-primary-soft, #e7f5f1);
  color: var(--rs-primary, #087f70);
}

.acceptance-content {
  min-height: 208px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(18px, 3vw, 34px);
  padding: 2px 0 16px;
}

.acceptance-ring {
  position: relative;
  width: 174px;
  height: 174px;
  flex: 0 0 174px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: conic-gradient(#4f86e8 var(--acceptance), #e8effb 0);
  filter: drop-shadow(0 10px 14px rgba(8, 127, 112, 0.12));
}

.acceptance-ring::before {
  content: '';
  position: absolute;
  inset: 11px;
  border: 1px solid rgba(215, 232, 227, 0.75);
  border-radius: 50%;
  background: var(--rs-surface, #fff);
}

.acceptance-ring-center {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 5px;
  text-align: center;
}

.acceptance-ring-center strong {
  color: var(--rs-ink, #123f45);
  font-size: 27px;
  letter-spacing: -0.045em;
}

.acceptance-ring-center span {
  color: var(--rs-muted, #6d8588);
  font-size: 10px;
  font-weight: 600;
}

.acceptance-summary {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  max-width: 190px;
}

.summary-icon {
  width: 34px;
  height: 34px;
  flex: 0 0 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: var(--rs-primary-soft, #e7f5f1);
  color: var(--rs-primary, #087f70);
}

.acceptance-summary strong {
  color: var(--rs-ink, #123f45);
  font-size: 12px;
  line-height: 1.5;
}

.acceptance-summary p {
  margin: 4px 0 0;
  color: var(--rs-muted, #6d8588);
  font-size: 11px;
}

.acceptance-footer {
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 9px;
  border-top: 1px solid var(--rs-border, #d7e8e3);
  color: var(--rs-muted, #6d8588);
  font-size: 10px;
}

.acceptance-footer span:not(.footer-divider) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.acceptance-footer strong {
  color: var(--rs-text, #284750);
  font-size: 11px;
}

.accepted-dot,
.other-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--rs-primary, #087f70);
}

.other-dot {
  background: #a7c9bf;
}

.footer-divider {
  width: 1px;
  height: 17px;
  margin: 0 3px;
  background: var(--rs-border, #d7e8e3);
}

.analytics-empty {
  min-height: 210px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
}

.empty-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
  border-radius: 14px;
  background: var(--rs-primary-soft, #e7f5f1);
  color: var(--rs-primary, #087f70);
}

.analytics-empty strong {
  color: var(--rs-ink, #123f45);
  font-size: 12px;
}

.analytics-empty p {
  margin: 6px 0 0;
  color: var(--rs-muted, #6d8588);
  font-size: 11px;
}

@media (max-width: 960px) {
  .panels.analytics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .analytics-card {
    min-height: auto !important;
    padding: 18px !important;
  }

  .acceptance-content {
    min-height: 190px;
    gap: 18px;
  }

  .acceptance-ring {
    width: 144px;
    height: 144px;
    flex-basis: 144px;
  }

  .acceptance-summary {
    max-width: 145px;
  }

  .acceptance-footer {
    flex-wrap: wrap;
    padding: 10px 0;
  }
}

.kpis h2 {
  color: var(--rs-primary, #087f70) !important;
}

.status-chart-card {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  min-height: 318px !important;
  display: flex;
  flex-direction: column;
  padding: 14px 15px !important;
  border: 1px solid var(--rs-border, #d7e8e3);
  border-radius: 12px !important;
  background: var(--rs-surface, #fff);
  box-shadow: 0 8px 22px rgba(18, 63, 69, 0.045);
}

.status-chart-header {
  margin-bottom: 8px;
}

.status-chart-header h2 {
  margin: 0;
  color: var(--rs-ink, #123f45);
  font-size: 13px;
  font-weight: 750;
  letter-spacing: -0.01em;
  text-transform: none;
}

.status-chart-content {
  flex: 1;
  min-height: 235px;
  display: grid;
  grid-template-columns: 140px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
}

.status-donut-wrap {
  display: grid;
  place-items: center;
}

.status-donut {
  position: relative;
  width: 138px;
  height: 138px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  box-shadow: 0 7px 15px rgba(8, 127, 112, 0.09);
}

.status-donut::before {
  content: '';
  position: absolute;
  width: 82px;
  height: 82px;
  border-radius: 50%;
  background: var(--rs-surface, #fff);
}

.status-donut-center {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 2px;
  text-align: center;
}

.status-donut-center span {
  color: var(--rs-muted, #6d8588);
  font-size: 9px;
}

.status-donut-center strong {
  color: var(--rs-ink, #123f45);
  font-size: 15px;
  font-weight: 800;
}

.status-legend {
  min-width: 0;
}

.status-legend-row {
  min-height: 32px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 28px 36px;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(215, 232, 227, 0.72);
  color: var(--rs-text, #284750);
  font-size: 9px;
}

.status-legend-row:last-child {
  border-bottom: 0;
}

.status-legend-name {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-legend-name i {
  width: 10px;
  height: 10px;
  flex: 0 0 10px;
  border-radius: 50%;
}

.status-legend-row strong {
  color: var(--rs-ink, #123f45);
  font-size: 9px;
  text-align: right;
}

.status-legend-row small {
  color: #78909f;
  font-size: 9px;
  text-align: right;
}

.status-chart-empty {
  min-height: 145px;
  display: grid;
  place-items: center;
  color: var(--rs-muted, #6d8588);
  font-size: 11px;
}

@media (max-width: 600px) {
  .status-chart-card {
    min-height: auto !important;
  }

  .status-chart-content {
    min-height: 190px;
    grid-template-columns: 112px minmax(0, 1fr);
    gap: 8px;
  }

  .status-donut {
    width: 108px;
    height: 108px;
  }

  .status-donut::before {
    width: 66px;
    height: 66px;
  }
}

.dashboard > .title {
  padding: 12px 16px;
}

.dashboard > .title h1 {
  font-size: 18px;
}

</style>
