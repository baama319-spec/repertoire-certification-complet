<script setup>
import LayoutReparateur from '../../layouts/LayoutReparateur.vue'
import CarteDemandeEntrante from '../../components/reparateur/CarteDemandeEntrante.vue'
import { demandes } from '../../donnees/demandes'
const selection = demandes[0]
</script>

<template>
  <LayoutReparateur>
    <section class="demandes-page">
      <section class="liste-demandes panneau">
        <header><h1>Demandes entrantes (4)</h1><button class="filtre">Filtrer :　Toutes　⌄</button></header>
        <div class="liste-scroll">
          <CarteDemandeEntrante v-for="demande in demandes" :key="demande.id" :demande="demande" :selectionnee="selection.id === demande.id" />
        </div>
      </section>

      <section class="detail-demande panneau">
        <h1>Détail de la demande <em>#{{ selection.id }}</em></h1>
        <article><h2><span>●</span> Client & localisation</h2><div class="client-lieu"><div><b>♟　 {{ selection.client }}</b><small>☎　 {{ selection.telephone }}</small></div><div><b>♦　 {{ selection.adresse }}</b></div></div></article>
        <article><h2><span>▣</span> Appareil & description de la panne</h2><div class="description"><p><b>Appareil :</b>　{{ selection.modele }}</p><p>▤　 "{{ selection.description }}"</p></div></article>
        <article><h2><span>⌕</span> Pièces jointes envoyées par le client</h2><div class="pieces"><figure><div class="ecran casse-1"></div><figcaption>▧　 ecran_casse_1.jpg</figcaption></figure><figure><div class="ecran casse-2"></div><figcaption>▧　 ecran_casse_2.jpg</figcaption></figure></div></article>
        <footer><h2>ϟ　 Action rapide <small>(ux traitement en 1 clic)</small></h2><div><button class="refuser">×　 Refuser la demande</button><button class="accepter">✓　 Accepter l'intervention</button></div></footer>
      </section>
    </section>
  </LayoutReparateur>
</template>

<style scoped>
.demandes-page{display:grid;grid-template-columns:46% 1fr;gap:18px;max-width:1334px;margin:auto}.panneau{background:#fff;border:1px solid #e1eaf6;border-radius:10px;box-shadow:0 2px 12px #1647820d}.liste-demandes{padding:16px}.liste-demandes header{height:47px;display:flex;justify-content:space-between;align-items:center;padding:0 9px 12px;border-bottom:1px solid #e5edf8}.liste-demandes h1,.detail-demande>h1{margin:0;text-transform:uppercase;font-size:18px;color:#0a3477}.filtre{height:40px;min-width:177px;border:1px solid #d4e3f9;border-radius:9px;background:#f8fbff;padding:0 15px;color:#244b86;font:600 13px inherit}.liste-scroll{max-height:681px;overflow:hidden;padding:16px 0 6px}.detail-demande{padding:16px 19px 14px;color:#17447f}.detail-demande>h1{padding:5px 6px 22px}.detail-demande>h1 em{color:#146df1;font-style:normal}.detail-demande article{border-bottom:1px solid #e8eef7;padding-bottom:14px;margin-bottom:11px}.detail-demande h2{display:flex;align-items:center;gap:13px;height:47px;margin:0;background:linear-gradient(100deg,#f0f6ff,#f8fbff);border-radius:9px;padding:0 13px;text-transform:uppercase;color:#0759ca;font-size:13px}.detail-demande h2 span{display:grid;place-items:center;width:38px;height:38px;background:#1375f5;border-radius:50%;color:#fff;font-size:18px}.client-lieu{display:grid;grid-template-columns:1fr 1.3fr;padding:16px 15px 5px;gap:18px}.client-lieu>div+div{border-left:1px solid #dbe7f6;padding-left:21px}.client-lieu b,.client-lieu small{display:block;font-size:13px;line-height:1.85}.client-lieu small{color:#174d96}.description{padding:13px 16px 5px;font-size:13px;line-height:1.5}.description p{margin:5px 0}.pieces{display:flex;gap:29px;padding:12px 17px 2px}.pieces figure{margin:0;width:202px;border:1px solid #dbe7f5;border-radius:6px;overflow:hidden}.ecran{height:106px;background:linear-gradient(135deg,#c79257,#e7c081 38%,#352f2e 39%,#0c111b 70%,#7e7e7d);position:relative}.ecran::after{content:'';position:absolute;inset:12px 28px;background:repeating-linear-gradient(48deg,transparent 0 18px,#d8e3ee88 19px 21px,transparent 22px 36px);transform:rotate(-6deg);border-radius:7px}.casse-2{background:linear-gradient(145deg,#3a4b60,#0a111b 57%,#b7956a)}.pieces figcaption{padding:10px;color:#255b9c;font-size:10px}footer{background:linear-gradient(100deg,#eef5ff,#f5f9ff);border-radius:8px;margin-top:13px;padding:12px 15px}footer h2{height:auto;background:transparent;padding:0;font-size:13px}footer h2 small{font-size:11px}footer>div{display:grid;grid-template-columns:1fr 1fr;gap:21px;margin-top:13px}footer button{height:46px;border-radius:8px;background:#fff;font-size:12px;font-weight:700}.refuser{border:1px solid #ff5362;color:#f13d4d}.accepter{border:1px solid #08ad78;background:linear-gradient(90deg,#09bc85,#00a36e);color:#fff;box-shadow:0 3px 6px #0eb17b33}@media(max-width:1100px){.demandes-page{grid-template-columns:43% 1fr}.detail-demande{padding:13px}.pieces figure{width:42%}}@media(max-width:850px){.demandes-page{grid-template-columns:1fr}.liste-scroll{max-height:440px}.detail-demande{min-width:0}}@media(max-width:500px){.client-lieu{grid-template-columns:1fr}.client-lieu>div+div{border:0;padding:0}.pieces{gap:8px;padding-left:0;padding-right:0}.pieces figure{width:49%}footer>div{grid-template-columns:1fr}.liste-demandes h1,.detail-demande>h1{font-size:14px}.filtre{min-width:115px}}
</style>
