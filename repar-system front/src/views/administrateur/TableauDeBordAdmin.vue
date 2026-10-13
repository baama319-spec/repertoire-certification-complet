<template>
  <AdministrationLayout>
    <section class="dashboard">
      <header class="title">
        <div><h1>Tableau de bord & statistiques</h1><p>Mise à jour à l’ouverture de cette page.</p></div>
      </header>
      <p v-if="erreur" class="feedback error" role="alert">{{ erreur }}</p>
      <p v-else-if="chargement" class="feedback">Chargement des statistiques…</p>
      <section class="kpis">
        <article v-for="kpi in kpis" :key="kpi.label" :class="kpi.color"><h2>{{ kpi.label }}</h2><strong>{{ formatter(kpi.value) }}</strong></article>
      </section>
      <section class="panels">
        <article class="panel distribution"><h2>Répartition des demandes par spécialité</h2><div v-if="chart.length" class="distribution-content"><div class="donut" :style="{ background: donutGradient }"><b>{{ formatter(statistiques.demandes_totales) }}<small>Total</small></b></div><div class="legend"><p v-for="item in chart" :key="item.name"><i :style="{background:item.color}"></i><span>{{ item.name }}</span><b>{{ item.percent }}<small>{{ formatter(item.count) }} demande(s)</small></b></p></div></div><p v-else class="empty">Aucune demande disponible pour le moment.</p></article>
        <article class="panel"><h2>Statistiques d'intervention</h2><div class="interventions"><div><span><AppIcon name="check-circle" :size="20"/></span><b>Taux d'acceptation</b><strong>{{ formatPercent(statistiques.taux_acceptation) }}</strong><small>{{ formatter(statistiques.demandes_acceptees) }} demande(s) acceptée(s) sur {{ formatter(statistiques.demandes_totales) }}</small></div></div></article>
      </section>
    </section>
  </AdministrationLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import AdministrationLayout from '../../components/administrateur/AdministrationLayout.vue'
import { chargerStatistiquesAdministration } from '../../services/serviceDemandes'

const statistiques = ref({ clients_inscrits: 0, reparateurs_actifs: 0, demandes_totales: 0, zones_couvertes: 0, demandes_acceptees: 0, taux_acceptation: 0, repartition_demandes: [] })
const chargement = ref(true)
const erreur = ref('')
const couleurs = ['#1477f8', '#8fe2b1', '#43b980', '#5799f2', '#086d68', '#91d9c3']
const formatter = valeur => new Intl.NumberFormat('fr-FR').format(Number(valeur) || 0)
const formatPercent = valeur => `${new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 1 }).format(Number(valeur) || 0)}%`
const kpis = computed(() => [
  { label: 'Clients inscrits', value: statistiques.value.clients_inscrits, color: 'blue' },
  { label: 'Réparateurs actifs', value: statistiques.value.reparateurs_actifs, color: 'green' },
  { label: 'Demandes totales', value: statistiques.value.demandes_totales, color: 'purple' },
  { label: 'Zones couvertes', value: statistiques.value.zones_couvertes, color: 'orange' },
])
const chart = computed(() => {
  const total = statistiques.value.demandes_totales || 0
  return statistiques.value.repartition_demandes.map((item, index) => ({
    name: item.nom,
    count: item.nombre,
    percent: formatPercent(total ? item.nombre / total * 100 : 0),
    color: couleurs[index % couleurs.length],
  }))
})
const donutGradient = computed(() => {
  let progression = 0
  const parts = chart.value.map(item => {
    const debut = progression
    progression += statistiques.value.demandes_totales ? item.count / statistiques.value.demandes_totales * 100 : 0
    return `${item.color} ${debut}% ${progression}%`
  })
  return `conic-gradient(${parts.join(', ')})`
})
onMounted(async () => {
  try { statistiques.value = await chargerStatistiquesAdministration() }
  catch (error) { erreur.value = error.message }
  finally { chargement.value = false }
})
</script>

<style scoped>
.dashboard{display:grid;gap:20px}.title,.panel{background:#fff;border:1px solid #e1edfa;border-radius:12px}.title{display:flex;align-items:center;gap:14px;padding:16px}.title-icon{width:54px;height:54px;display:grid;place-items:center;background:#e5f4f0;border-radius:12px;color:#087f70;font-size:28px}.title h1{text-transform:uppercase;margin:0;font-size:20px}.title p{margin:7px 0 0;color:#5576ad}.title aside{margin-left:auto;display:flex;gap:10px;padding:10px 14px;background:#f5faff;border:1px solid #ddebfc;border-radius:10px;color:#4471b3;font-size:12px}.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}.kpis article{min-height:137px;padding:18px;border:1px solid #dceeea;border-radius:10px;background:#fff}.kpis article>span{float:left;width:48px;height:48px;display:grid;place-items:center;border-radius:14px;color:#fff;background:#087f70;font-size:24px;margin-right:14px}.kpis h2{font-size:14px;margin:8px 0}.kpis strong{display:block;font-size:28px;margin-top:18px}.kpis small{display:block;color:#00a879;font-weight:800;margin-top:12px}.kpis small i{font-style:normal;color:#6280b1;margin-left:14px;font-weight:400}.kpis .green>span{background:#29b873}.purple>span{background:#7548e8!important}.orange>span{background:#ff7d2b!important}.panels{display:grid;grid-template-columns:1.1fr .95fr;gap:20px}.panel{padding:16px}.panel h2{margin:0;color:#174b50;font-size:15px;text-transform:uppercase}.distribution-content{display:flex;align-items:center;gap:36px;padding:25px}.donut{width:195px;height:195px;flex:none;border-radius:50%;display:grid;place-items:center;background:conic-gradient(#1976ef 0 45%,#ff8243 45% 80%,#34b879 80%)}.donut b{width:100px;height:100px;background:#fff;border-radius:50%;display:grid;place-content:center;text-align:center;font-size:20px}.donut small,.legend small{display:block;font-weight:400;color:#6682b2;font-size:11px;margin-top:5px}.legend{flex:1}.legend p{display:flex;align-items:center;gap:10px;border-bottom:1px solid #e5effa;padding:13px 0;margin:0}.legend i{width:17px;height:17px;border-radius:50%}.legend span{font-weight:700}.legend b{margin-left:auto;text-align:right}.interventions{margin-top:24px}.interventions>div{border:1px solid #d8ebe8;border-radius:9px;padding:15px;min-height:193px}.interventions span{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:50%;background:#29b873;color:#fff;font-size:21px;margin-right:10px}.interventions b{vertical-align:top;line-height:40px;color:#078157;font-size:13px}.interventions strong{display:block;font-size:31px;margin:25px 0 13px;text-align:center}.interventions small{color:#00a879}.requests header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}.requests a{color:#087f70;border:1px solid #cde2ff;border-radius:18px;padding:9px 13px;font-size:12px;font-weight:700}.request-head,.request{display:grid;grid-template-columns:1.1fr 1.2fr 1.1fr 1.1fr 1.4fr 1fr 1.15fr;align-items:center;gap:8px;padding:14px;font-size:12px}.request-head{background:#edf8f5;text-transform:uppercase;color:#416bb0;font-size:10px;font-weight:800}.request{border-bottom:1px solid #e4eef9;color:#345890}.request em,mark{font-style:normal;padding:7px 10px;border-radius:14px;width:max-content;background:#e2efff;color:#087f70}.request mark{background:#fff3dc;color:#e38b00}.request mark.accepted{background:#ddf8ee;color:#00a775}.request button{background:#fff;border:1px solid #8fc1ff;color:#087f70;border-radius:7px;padding:8px;font-size:11px}.none{text-align:center;color:#6580af}@media(max-width:1050px){.kpis{grid-template-columns:repeat(2,1fr)}.panels{grid-template-columns:1fr}.request-head,.request{min-width:900px}.requests{overflow:auto}}@media(max-width:600px){.title{align-items:flex-start}.title h1{font-size:16px}.title aside{display:none}.kpis{grid-template-columns:1fr}.distribution-content{padding:18px;gap:14px}.donut{width:150px;height:150px}.legend p{font-size:12px}}
.kpis article{min-height:112px}.kpis h2{margin:0;color:#5576ad}.kpis strong{margin-top:24px}
.panels > .panel{min-height:390px}
.feedback{margin:0;padding:12px 14px;border-radius:8px;background:#eef8f5;color:#087f70}.feedback.error{background:#fff0f2;color:#c22f45}.empty{padding:52px 20px;text-align:center;color:#6682b2}

/* Graphique des spécialités : présentation compacte inspirée du visuel de référence. */
.panels > .distribution {
  align-self: start;
  min-height: 180px;
  padding: 12px 14px;
  border-radius: 9px;
}

.panel.distribution h2 {
  color: #173f4d;
  font-size: 13px;
  font-weight: 800;
  text-transform: none;
}

.distribution-content {
  min-height: 130px;
  gap: 22px;
  padding: 10px 8px 0;
}

.distribution .donut {
  width: 96px;
  height: 96px;
}

.distribution .donut b {
  width: 58px;
  height: 58px;
  color: #153d4c;
  font-size: 15px;
}

.distribution .donut small,
.distribution .legend small {
  margin-top: 3px;
  font-size: 10px;
}

.distribution .legend p {
  min-height: 40px;
  gap: 10px;
  padding: 6px 0;
  color: #294e5c;
  font-size: 11px;
}

.distribution .legend i {
  width: 10px;
  height: 10px;
  flex: 0 0 10px;
}

.distribution .legend span {
  font-size: 11px;
  font-weight: 700;
}

.distribution .legend b {
  min-width: 68px;
  font-size: 12px;
}

.distribution .legend small {
  color: #6b85a5;
  font-weight: 400;
}

@media (max-width: 600px) {
  .panels > .distribution {
    min-height: auto;
  }

  .distribution-content {
    gap: 14px;
    padding: 12px 2px 0;
  }

  .distribution .donut {
    width: 88px;
    height: 88px;
  }
}
</style>
