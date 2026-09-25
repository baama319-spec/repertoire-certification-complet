<template>
  <aside class="admin-sidebar">
    <RouterLink class="admin-brand" to="/admin"><span class="brand-tool">🛠</span><strong>ReparSystem</strong><small>ADMIN</small></RouterLink>
    <nav>
      <component v-for="item in items" :key="item.label" :is="item.disabled ? 'button' : 'RouterLink'" :to="item.disabled ? undefined : item.to" :class="{ disabled: item.disabled }"><span>{{ item.icon }}</span>{{ item.label }}</component>
    </nav>
    <div class="admin-sidebar-bottom"><span>▥</span><strong>ReparSystem ADMIN</strong><p>Une plateforme plus fiable,<br>plus proche de vous.</p></div>
  </aside>
</template>
<script setup>
const items = [
  { label: 'Statistiques', icon: '▥', to: '/admin' }, { label: 'Réparateurs', icon: '🛠', to: '/admin/reparateurs' },
  { label: 'Clients', icon: '♙', to: '/admin/clients' }, { label: 'Demandes', icon: '▣', to: '/admin/demandes' },
  { label: 'Catégories', icon: '◆', to: '/admin/categories' }, { label: 'Zones Interv.', icon: '●', to: '/admin/zones' }, { label: 'Paramètres', icon: '⚙', to: '/admin', disabled: true },
]
</script>
<style scoped>
.admin-sidebar{width:296px;min-height:100vh;flex:none;display:flex;flex-direction:column;background:linear-gradient(160deg,#0d315f,#051b3a);color:#fff}.admin-brand{height:80px;padding:0 20px;display:flex;align-items:center;gap:12px;color:#fff;background:#15535a;border-radius:0 0 28px 0;font-size:27px}.brand-tool{font-size:31px}.admin-brand small{font-size:12px;background:#087f70;padding:6px 9px;border-radius:7px}nav{padding:24px 14px}nav a,nav button{width:100%;height:61px;display:flex;align-items:center;gap:25px;padding:0 22px;border-radius:9px;color:#f4f8ff;font-weight:600;font-size:15px;text-align:left;background:transparent}nav a span,nav button span{width:24px;text-align:center;font-size:22px}nav a.router-link-exact-active{background:#087f70;box-shadow:0 8px 18px #0065df55}nav button.disabled{cursor:default}.admin-sidebar-bottom{margin:auto 25px 80px;text-align:center;color:#dceaff}.admin-sidebar-bottom>span{display:block;color:#087f70;font-size:58px;margin-bottom:15px}.admin-sidebar-bottom strong{display:block;font-size:17px}.admin-sidebar-bottom p{font-size:13px;line-height:1.55;margin:8px 0}@media(max-width:850px){.admin-sidebar{width:72px}.admin-brand{padding:0;justify-content:center;height:72px;border-radius:0}.admin-brand strong,.admin-brand small,.admin-sidebar-bottom{display:none}nav{padding:12px 6px}nav a,nav button{padding:0;justify-content:center;height:55px}nav a span,nav button span{font-size:20px}}
</style>
