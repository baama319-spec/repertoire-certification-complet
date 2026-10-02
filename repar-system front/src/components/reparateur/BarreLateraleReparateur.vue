<template>
  <aside class="sidebar-pro">
    <RouterLink class="pro-logo" to="/pro/demandes"><MarqueDashboard role="Pro" :size="58" :text-size="23" /></RouterLink>
    <nav>
      <RouterLink to="/pro/demandes"><IconeDashboard name="requests" /> Demandes <strong>4</strong></RouterLink>
      <RouterLink to="/pro/realisations"><IconeDashboard name="portfolio" /> Réalisations</RouterLink>
      <RouterLink to="/pro/avis"><IconeDashboard name="reviews" /> Avis clients</RouterLink>
      <RouterLink to="/pro/profil"><IconeDashboard name="profile" /> Mon Profil</RouterLink>
    </nav>
  </aside>
</template>

<script setup>
import MarqueDashboard from '../commun/MarqueDashboard.vue'
import IconeDashboard from '../commun/IconeDashboard.vue'
</script>

<style scoped>
.sidebar-pro{width:299px;min-height:100vh;display:flex;flex-direction:column;background:radial-gradient(circle at 78% 10%,#143d84,#061d40 55%,#04152f);color:#fff;padding:18px 16px}.pro-logo{display:flex;align-items:center;min-height:66px;padding:0 2px;color:#fff;text-decoration:none}.sidebar-pro nav{display:grid;gap:15px;margin-top:47px}.sidebar-pro nav a{height:58px;display:flex;align-items:center;gap:18px;padding:0 20px;border-radius:8px;color:#f2f6ff;font-size:15px;font-weight:600}.sidebar-pro nav a.router-link-active{background:linear-gradient(115deg,#1476ff,#1261e5);box-shadow:0 7px 15px #001a4c}.sidebar-pro nav :deep(.dashboard-icon){width:21px;height:21px;opacity:.93}.sidebar-pro nav strong{display:grid;place-items:center;margin-left:auto;width:27px;height:27px;border-radius:50%;background:white;color:#1268e5;font-size:13px}@media(max-width:800px){.sidebar-pro{width:62px;padding:16px 8px}.pro-logo{padding:0;overflow:hidden;width:46px;min-height:48px;justify-content:center}.pro-logo :deep(.dashboard-brand){gap:0}.pro-logo :deep(.dashboard-brand-label){display:none}.pro-logo :deep(.brand-tile){width:46px;height:46px;flex-basis:46px}.sidebar-pro nav a{padding:0;justify-content:center;font-size:0}.sidebar-pro nav :deep(.dashboard-icon){width:21px;height:21px}.sidebar-pro nav strong{position:absolute;margin:0 0 20px 23px}}
</style>
