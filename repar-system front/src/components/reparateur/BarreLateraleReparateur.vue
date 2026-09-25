<template>
  <aside class="sidebar-pro">
    <RouterLink class="pro-logo" to="/pro/demandes"><span>⚒</span> ReparSystem <b>Pro</b></RouterLink>
    <nav>
      <RouterLink to="/pro/demandes"><i>▣</i> Demandes <strong>4</strong></RouterLink>
      <RouterLink to="/pro/realisations"><i>▧</i> Réalisations</RouterLink>
      <RouterLink to="/pro/avis"><i>★</i> Avis clients</RouterLink>
      <RouterLink to="/pro/profil"><i>⚙</i> Mon Profil</RouterLink>
    </nav>
    <div class="service-note"><div>♙</div><b>Des experts à votre service</b><small>Réparez aujourd'hui, profitez demain</small></div>
  </aside>
</template>

<style scoped>
.sidebar-pro{width:299px;min-height:100vh;display:flex;flex-direction:column;background:radial-gradient(circle at 78% 10%,#143d84,#061d40 55%,#04152f);color:#fff;padding:18px 16px}.pro-logo{display:flex;align-items:center;gap:11px;padding:0 6px;color:#fff;font-size:27px;font-weight:700;letter-spacing:-1px;white-space:nowrap}.pro-logo span{font-size:36px;color:#fff}.pro-logo b{font-weight:400}.sidebar-pro nav{display:grid;gap:15px;margin-top:47px}.sidebar-pro nav a{height:58px;display:flex;align-items:center;gap:22px;padding:0 20px;border-radius:8px;color:#f2f6ff;font-size:15px;font-weight:600}.sidebar-pro nav a.router-link-active{background:linear-gradient(115deg,#1476ff,#1261e5);box-shadow:0 7px 15px #001a4c}.sidebar-pro nav i{font-style:normal;font-size:24px}.sidebar-pro nav strong{display:grid;place-items:center;margin-left:auto;width:27px;height:27px;border-radius:50%;background:white;color:#1268e5;font-size:13px}.service-note{margin:auto 0 82px;text-align:center;color:#d6e4ff}.service-note div{font-size:72px;color:#1977ff}.service-note b{display:block;margin-top:14px;font-size:13px}.service-note small{display:block;margin-top:9px;font-size:11px;color:#9bb3db}@media(max-width:800px){.sidebar-pro{width:62px;padding:16px 8px}.pro-logo{padding:0;overflow:hidden;width:36px;font-size:0}.pro-logo span{font-size:25px}.sidebar-pro nav a{padding:0;justify-content:center;font-size:0}.sidebar-pro nav i{font-size:19px}.sidebar-pro nav strong{position:absolute;margin:0 0 20px 23px}.service-note{display:none}}
</style>
