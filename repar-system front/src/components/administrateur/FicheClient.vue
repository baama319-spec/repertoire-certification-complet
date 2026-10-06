<template>
  <div class="overlay" @click.self="$emit('close')">
    <article class="sheet">
      <header><span class="badge"><AppIcon name="users" :size="18"/></span><h2>FICHE CLIENT &amp; HISTORIQUE : {{client.name.toUpperCase()}}</h2><button aria-label="Fermer" @click="$emit('close')"><AppIcon name="close" :size="20"/></button></header>
      <main>
        <div class="top">
          <section class="left">
            <div class="identity card"><img :src="client.image" :alt="client.name"><div><h3>{{client.name}}</h3><mark><AppIcon name="circle" :size="10" fill="currentColor"/> Actif</mark><small>ID : {{client.id}}</small></div></div>
            <div class="stats card"><p><AppIcon name="clipboard" :size="20"/><span>Total des demandes<b>{{client.requests}}</b></span></p><p><AppIcon name="clock" :size="20"/><span>Dernière demande<b>10/09/2026</b></span></p></div>
          </section>
          <section class="personal card"><h4><AppIcon name="user" :size="15"/> INFORMATIONS PERSONNELLES</h4><dl><dt><AppIcon name="user" :size="14"/> Nom complet :</dt><dd>{{client.name}}</dd><dt><AppIcon name="phone" :size="14"/> Téléphone :</dt><dd>{{client.phone}}</dd><dt><AppIcon name="mail" :size="14"/> Email :</dt><dd>{{client.email}}</dd><dt><AppIcon name="pin" :size="14"/> Adresse :</dt><dd>Rue 10 × Boulevard de la République,<br>Dakar Plateau</dd><dt><AppIcon name="calendar" :size="14"/> Date d'inscription :</dt><dd>12 Janvier 2026</dd></dl></section>
        </div>
        <section class="history card"><h3><AppIcon name="clock" :size="16"/> HISTORIQUE DES DEMANDES DE RÉPARATION (5 TOTAL)</h3><p>Voici la liste complète des demandes effectuées par ce client.</p><div class="table"><table><thead><tr><th>ID DEMANDE</th><th>DATE</th><th>APPAREIL / PANNE</th><th>RÉPARATEUR</th><th>STATUT</th><th></th></tr></thead><tbody><tr v-for="request in requests" :key="request.id"><td><b>{{request.id}}</b></td><td>{{request.date}}</td><td><AppIcon :name="request.icon" :size="15"/> <b>{{request.device}}</b><small>{{request.issue}}</small></td><td><AppIcon name="wrench" :size="14"/> {{request.pro}}</td><td><mark :class="request.status==='Terminé'?'done':''"><AppIcon :name="request.status==='Terminé'?'check-circle':'clock'" :size="14"/> {{request.status}}</mark></td><td><button><AppIcon name="info" :size="14"/> Voir détail</button></td></tr></tbody></table></div></section>
      </main>
      <footer><button @click="$emit('block')"><AppIcon name="x-circle" :size="15"/> Bloquer ce client</button></footer>
    </article>
  </div>
</template>
<script setup>
defineProps({client:{type:Object,required:true}})
defineEmits(['close','block'])
const requests=[{id:'#D-2026-089',date:'10/09/2026',icon:'smartphone',device:'Smartphone',issue:'(Écran brisé)',pro:'Awa Diop',status:'En attente'},{id:'#D-2026-042',date:'15/06/2026',icon:'laptop',device:'PC Portable',issue:'(Clavier HS)',pro:'Ousmane Sow',status:'Terminé'},{id:'#D-2026-011',date:'02/03/2026',icon:'television',device:'TV Samsung',issue:'(Alimentation)',pro:'Awa Diop',status:'Terminé'}]
</script>
