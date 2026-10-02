<template>
  <aside class="admin-sidebar">
    <RouterLink class="admin-brand" to="/admin"><MarqueDashboard role="Admin" :size="56" :text-size="20" /></RouterLink>
    <nav>
      <component v-for="item in items" :key="item.label" :is="item.disabled ? 'button' : 'RouterLink'" :to="item.disabled ? undefined : item.to" :class="{ disabled: item.disabled }"><IconeDashboard :name="item.icon" />{{ item.label }}</component>
    </nav>
  </aside>
</template>
<script setup>
import MarqueDashboard from '../commun/MarqueDashboard.vue'
import IconeDashboard from '../commun/IconeDashboard.vue'

const items = [
  { label: 'Statistiques', icon: 'overview', to: '/admin' }, { label: 'Réparateurs', icon: 'repairers', to: '/admin/reparateurs' },
  { label: 'Clients', icon: 'clients', to: '/admin/clients' }, { label: 'Demandes', icon: 'requests', to: '/admin/demandes' },
  { label: 'Catégories', icon: 'categories', to: '/admin/categories' }, { label: 'Zones Interv.', icon: 'zones', to: '/admin/zones' }, { label: 'Paramètres', icon: 'settings', to: '/admin', disabled: true },
]
</script>
<style scoped>
.admin-sidebar{width:296px;min-height:100vh;flex:none;display:flex;flex-direction:column;background:linear-gradient(160deg,#0d315f,#051b3a);color:#fff}.admin-brand{height:90px;padding:0 18px;display:flex;align-items:center;gap:12px;color:#fff;background:transparent;border-radius:0;text-decoration:none}nav{padding:24px 14px}nav a,nav button{width:100%;height:61px;display:flex;align-items:center;gap:18px;padding:0 22px;border-radius:9px;color:#f4f8ff;font-weight:600;font-size:15px;text-align:left;background:transparent}nav :deep(.dashboard-icon){width:22px;height:22px;opacity:.92}nav a.router-link-exact-active{background:#087f70;box-shadow:0 8px 18px #0065df55}nav button.disabled{cursor:default}@media(max-width:850px){.admin-sidebar{width:72px}.admin-brand{height:72px;padding:0;justify-content:center;border-radius:0}.admin-brand :deep(.dashboard-brand){gap:0}.admin-brand :deep(.dashboard-brand-label){display:none}.admin-brand :deep(.brand-tile){width:48px;height:48px;flex-basis:48px}nav{padding:12px 6px}nav a,nav button{padding:0;justify-content:center;height:55px}nav :deep(.dashboard-icon){width:22px;height:22px}}
</style>
