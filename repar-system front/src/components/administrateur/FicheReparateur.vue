<template>
  <div class="overlay" @click.self="$emit('close')"><article class="sheet" role="dialog" aria-modal="true">
    <header><h2>FICHE &amp; VÉRIFICATION RÉPARATEUR : {{ reparateur.name.toUpperCase() }}</h2><button class="close" aria-label="Fermer" @click="$emit('close')"><AppIcon name="close" :size="20"/></button></header>
    <div class="body"><section class="left">
      <section class="card identity"><img v-if="photoVisible" :src="reparateur.image" :alt="`Photo de ${reparateur.name}`" @error="photoVisible = false"><span v-else class="identity-avatar">{{ initiales }}</span><div><h3>{{ reparateur.name }} <small :class="statusClass">{{ reparateur.status }}</small></h3><p>Réparateur professionnel</p><strong v-if="reparateur.nombreAvis"><AppIcon v-for="star in 5" :key="star" name="star" :size="14" fill="currentColor"/> <b>{{ reparateur.noteMoyenne.toFixed(1) }}</b> / 5 <em>({{ reparateur.nombreAvis }} avis)</em></strong><span v-else class="no-rating">Aucun avis pour le moment</span></div></section>
      <section class="card info"><h4>INFORMATIONS PERSONNELLES &amp; CONTACT</h4><dl><dt>Nom complet</dt><dd>{{ reparateur.name }}</dd><dt>Téléphone</dt><dd>{{ reparateur.phone }}</dd><dt>Email</dt><dd>{{ reparateur.email }}</dd></dl></section>
      <section class="card presentation"><h4>PRÉSENTATION</h4><p>{{ reparateur.description || 'Non renseignée' }}</p></section>
      <section class="card info"><h4>COMPÉTENCES &amp; COUVERTURE GÉOGRAPHIQUE</h4><dl><dt>Spécialités</dt><dd>{{ reparateur.specialties.length ? reparateur.specialties.join(', ') : 'Non renseignées' }}</dd><dt>Zones d’intervention</dt><dd>{{ reparateur.zones.length ? reparateur.zones.join(', ') : 'Non renseignées' }}</dd><dt>Expérience déclarée</dt><dd>{{ reparateur.experience ?? 0 }} an(s)</dd></dl></section>
      <section class="card documents"><h4>PIÈCES JUSTIFICATIVES</h4>
        <div v-if="reparateur.carteIdentite" class="document-item"><img v-if="carteEstImage && carteImageVisible" class="document-preview" :src="reparateur.carteIdentite" alt="Aperçu de la carte d’identité" @error="carteImageVisible = false"><span v-else class="document-placeholder"><AppIcon name="document" :size="20"/></span><span class="tag">Carte d’identité</span><a :href="reparateur.carteIdentite" target="_blank" rel="noreferrer">Voir le document</a></div>
        <div v-if="reparateur.documents && reparateur.documents.length" class="documents-list">
          <div v-for="doc in reparateur.documents" :key="doc.id" class="document-item"><img v-if="doc.estImage && !imagesEnErreur.has(doc.id)" class="document-preview" :src="doc.document" :alt="`Aperçu de ${doc.nomFichier}`" @error="signalerImageEnErreur(doc.id)"><span v-else class="document-placeholder"><AppIcon name="document" :size="20"/></span><span class="tag">{{ doc.type }}</span><a :href="doc.document" target="_blank" rel="noreferrer">{{ doc.nomFichier || 'Voir le document' }}</a></div>
        </div>
        <p v-if="!reparateur.carteIdentite && !reparateur.documents?.length" class="sans-document">Aucune pièce justificative n’a été ajoutée.</p>
      </section><button class="refuse" @click="choice='Refusée'">Refuser / Incomplet</button>
    </section><section class="right">
      <section class="card account"><p><span><small>ID Réparateur</small><b>#{{ reparateur.id }}</b></span></p><p><span><small>Membre depuis</small><b>{{ dateMembre }}</b></span></p><p><span><small>Statut du compte</small><b>{{ reparateur.compteActif ? 'Actif' : 'Bloqué' }}</b></span></p></section>
      <section class="card certification"><h4>STATUT DE CANDIDATURE</h4><b>Statut actuel</b><mark :class="statusClass">{{ reparateur.status }}</mark><p>Le statut et la décision reflètent les informations actuelles du profil.</p></section>
      <section class="card actions"><h4>VALIDATION DE CANDIDATURE</h4><div class="action status"><span><b>DÉCISION</b><small><button :class="{chosen:choice==='Refusée'}" @click="choice='Refusée'">Refuser</button><button :class="{chosen:choice==='Validée'}" @click="choice='Validée'">Valider</button></small></span></div><p class="green">Valider accepte la candidature, sans attribuer la certification Pro.</p><label>COMMENTAIRE / MOTIF DE REFUS<textarea v-model="comment" maxlength="500" placeholder="Motif ou commentaire de vérification..."></textarea><small>{{comment.length}}/500</small></label></section><button class="validate" :disabled="!choice" @click="valider">Enregistrer la validation</button><button v-if="reparateur.statutVerification === 'VALIDEE' && !reparateur.profilVerifie" class="validate" @click="$emit('certify')">Certifier Pro</button>
    </section></div>
  </article></div>
</template>
<script setup>
import { computed, ref, watch } from 'vue'
const props=defineProps({reparateur:{type:Object,required:true}});const emit=defineEmits(['close','validate','certify'])
const choice=ref(props.reparateur.statutVerification === 'REFUSEE' ? 'Refusée' : props.reparateur.statutVerification === 'VALIDEE' ? 'Validée' : ''),comment=ref('')
const photoVisible=ref(true)
watch(() => props.reparateur.image, () => { photoVisible.value = true })
const carteImageVisible=ref(true)
const imagesEnErreur=ref(new Set())
const signalerImageEnErreur=id => { imagesEnErreur.value = new Set([...imagesEnErreur.value, id]) }
const initiales=computed(() => props.reparateur.name.split(/\s+/).filter(Boolean).slice(0,2).map(part => part[0]).join('').toUpperCase() || 'R')
const dateMembre=computed(() => {
  if (!props.reparateur.membreDepuis) return 'Non renseignée'
  const date = new Date(props.reparateur.membreDepuis)
  return Number.isNaN(date.getTime()) ? 'Non renseignée' : new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(date)
})
const carteEstImage=computed(() => /\.(jpe?g|png|webp|gif|bmp|avif)(?:$|\?)/i.test(props.reparateur.carteIdentite || ''))
const statusClass=computed(() => ({'Compte bloqué': 'blocked', 'Certifié Pro': 'certified', 'Validée': 'validated', 'Refusée': 'rejected', 'En attente': 'pending'}[props.reparateur.status] || 'pending'))
const valider = () => { if (choice.value) emit('validate', { statut: choice.value === 'Validée' ? 'VALIDEE' : 'REFUSEE', motif: comment.value }) }
</script>
<style scoped>
.overlay{position:fixed;z-index:50;inset:0;background:#0a315b73;backdrop-filter:blur(3px);display:grid;place-items:center;padding:28px}.sheet{width:min(1120px,100%);max-height:calc(100vh - 56px);overflow:auto;background:#fff;border-radius:12px;box-shadow:0 24px 55px #031e3d55;color:#15535a}.sheet>header{height:76px;display:flex;align-items:center;gap:18px;padding:0 28px;border-bottom:1px solid #dceeea}.head-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:12px;background:#087f70;color:#fff;font-size:22px}.sheet h2{margin:0;font-size:18px}.close{margin-left:auto;background:transparent;color:#0d7a66;font-size:30px;font-weight:400}.body{display:grid;grid-template-columns:1.28fr .96fr;gap:17px;padding:21px 22px 18px}.left,.right{display:grid;align-content:start;gap:11px}.card{border:1px solid #d9efe7;border-radius:8px;background:#fff;overflow:hidden}.identity{height:144px;padding:12px;display:flex;align-items:center;gap:20px}.identity img{width:105px;height:105px;border-radius:50%;object-fit:cover}.identity h3{margin:0;font-size:19px;color:#174b50}.identity h3 small{vertical-align:middle;margin-left:8px;padding:5px 10px;background:#d6f8e8;color:#00a66c;border-radius:15px;font-size:10px}.identity p{margin:10px 0 15px;font-size:14px}.identity strong{color:#ff9c00;font-size:20px;letter-spacing:1px}.identity strong b{color:#15535a;margin-left:6px}.identity strong em{color:#1a8d74;font-size:12px;font-style:normal;font-weight:500;letter-spacing:0}.info{padding:12px 15px 11px}.card h4{height:34px;margin:-12px -15px 10px;padding:10px 15px;border-bottom:1px solid #dfeee8;font-size:12px}.info dl{display:grid;grid-template-columns:152px 1fr;gap:11px;margin:0;font-size:11px}.info dt{color:#277d69}.info dd{margin:0;color:#15535a;font-weight:600}.documents{padding:12px}.documents h4{margin:-12px -12px 8px;padding-left:12px}.document{height:67px;display:flex;align-items:center;gap:12px;border-bottom:1px solid #e4f3ee;padding:7px 0}.document img{width:66px;height:46px;object-fit:cover;border:1px solid #d5eadf;border-radius:3px}.document div{flex:1;min-width:0}.document b,.document small{display:block;font-size:10px}.document b{color:#15535a}.document small{color:#2a876d;margin-top:6px}.document mark,.action mark{background:#d8f9e9;color:#00a875;border:0;border-radius:15px;padding:5px 11px;font-size:10px}.document button{min-width:69px;background:#fff;border:1px solid #3ba67f;color:#0a7f68;border-radius:7px;padding:8px;font-size:10px}.refuse,.validate{height:40px;width:205px;border-radius:7px;background:#fff0f2;border:1px solid #ff8293;color:#fa2743;font-size:11px}.account{padding:12px 17px;background:#f6fbf8;border:1px solid #d3eee2;border-radius:8px}.account p{display:flex;gap:19px;margin:0 0 13px;font-size:19px;color:#087f70}.account p:last-child{margin-bottom:1px}.account small,.account b{display:block}.account small{color:#2b8d74;font-size:11px;margin-bottom:4px}.account b{color:#15535a;font-size:12px}.certification{padding:12px 15px 17px}.certification h4,.actions h4{margin:-12px -15px 15px}.certification>b{display:block;font-size:12px;margin-bottom:9px}.certification mark{display:inline-block;border:0;border-radius:18px;background:#fff0d3;color:#f39300;padding:9px 15px;font-weight:700}.certification mark.certified{background:#d8f9e9;color:#00a875}.certification p,.green{margin:13px 0 0;border:1px solid #cfeee0;border-radius:6px;background:#edfdf5;padding:12px;color:#0c7c63;font-size:11px;line-height:1.55}.actions{padding:12px 15px 20px}.action{min-height:60px;display:flex;align-items:flex-start;gap:12px;border-bottom:1px solid #e4f3ee;padding:2px 3px 10px}.action i{display:grid;place-items:center;width:19px;height:19px;border-radius:50%;background:#08ab6b;color:#fff;font-style:normal;font-size:11px}.action span{flex:1}.action b,.action small{display:block;font-size:10px}.action b{margin-bottom:8px}.action small{color:#2d8e76}.action mark{margin-top:16px}.status{padding-top:12px;min-height:80px}.status small{display:flex;gap:10px;margin-top:9px}.status button{width:135px;height:31px;border-radius:8px;border:1px solid #bfe5d5;background:#fff;color:#2b8d74;font-size:10px}.status button:last-child{border-color:#5cc8a1;background:#e4fbf0;color:#0d8f69}.status button.chosen{box-shadow:inset 0 0 0 1px currentColor}.green{background:#e7fbf2;border-color:#c6f0de;color:#009c62;font-size:10px}.actions label{position:relative;display:block;margin:15px 2px 0;font-size:10px}.actions textarea{display:block;width:100%;height:63px;resize:none;margin-top:8px;border:1px solid #bfe5d5;border-radius:6px;padding:10px;font:inherit;font-size:10px;outline-color:#0d8f69}.actions label>small{position:absolute;right:7px;bottom:6px;color:#2b8d74;font-size:9px}.validate{justify-self:end;width:225px;background:#06a866;border-color:#06a866;color:#fff}@media(max-width:850px){.overlay{padding:12px;align-items:start}.sheet{max-height:calc(100vh - 24px)}.body{grid-template-columns:1fr}.sheet h2{font-size:14px}}@media(max-width:480px){.sheet>header{height:66px;padding:0 14px;gap:10px}.head-icon{width:34px;height:34px}.sheet h2{font-size:11px}.body{padding:12px}.identity{gap:11px}.identity img{width:75px;height:75px}.identity h3{font-size:14px}.identity strong{font-size:13px}.document mark{display:none}.status small{gap:5px}.status button{width:50%;font-size:9px}}
.account { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); align-items:start; gap:12px; padding:16px; background:#f5fbf8; border:1px solid #d7efe7; border-radius:8px; }
.presentation { padding:12px 15px; }
.presentation h4 { margin:-12px -15px 10px; }
.presentation p { margin:0; color:#15535a; font-size:12px; line-height:1.55; overflow-wrap:anywhere; }
.account p { display:block; align-self:start; min-width:0; margin:0; padding:0; font-size:12px; color:#15535a; }
.account span { display:grid; grid-template-rows:18px auto; align-content:start; align-items:start; gap:4px; }
.account small { display:block; height:18px; min-height:18px; margin:0; padding:0; color:#2a8d74; font-size:11px; line-height:18px; white-space:nowrap; }
.account b { display:block; margin:0; padding:0; color:#15535a; font-size:12px; line-height:16px; white-space:nowrap; }
@media(max-width:600px) { .account { grid-template-columns:1fr; gap:12px; } .account span { display:flex; flex-direction:row; align-items:center; justify-content:space-between; } .account small { height:auto; min-height:0; line-height:1.25; } }

.identity img,
.identity-avatar {
  width: 105px;
  height: 105px;
  flex: 0 0 105px;
  border: 1px solid #e3efec;
  border-radius: 50%;
  background: #eef8f5;
  object-fit: cover;
}

.identity-avatar {
  display: grid;
  place-items: center;
  color: #087f70;
  font-size: 30px;
  font-weight: 800;
}

.identity h3 small.pending { background: #fff1d8; color: #a86700; }
.identity h3 small.rejected,
.identity h3 small.blocked { background: #ffe7ec; color: #c22f45; }
.identity h3 small.validated,
.identity h3 small.certified { background: #dff8ef; color: #008b68; }
.no-rating { color: #71849b; font-size: 12px; }

.documents-list { display: grid; gap: 8px; }
.documents .document-item {
  display: grid;
  grid-template-columns: 76px minmax(90px, auto) minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  min-height: 72px;
  padding: 8px;
  border: 1px solid #e2eceb;
  border-radius: 9px;
  background: #fbfdfd;
}

.document-preview,
.document-placeholder {
  width: 76px;
  height: 60px;
  border: 1px solid #dce7e8;
  border-radius: 7px;
  background: #fff;
  object-fit: contain;
}

.document-placeholder { display: grid; place-items: center; color: #087f70; }
.documents .tag { margin: 0; color: #526277; font-size: 11px; }
.documents .document-item a { min-width: 0; overflow-wrap: anywhere; color: #087f70; font-size: 12px; font-weight: 600; }
.documents .document-item a:hover { text-decoration: underline; }
.sans-document { color: #71849b; font-size: 12px; }
.certification mark.pending { background: #fff1d8; color: #a86700; }
.certification mark.rejected,
.certification mark.blocked { background: #ffe7ec; color: #c22f45; }
.certification mark.validated,
.certification mark.certified { background: #dff8ef; color: #008b68; }
.validate:disabled { opacity: .5; cursor: not-allowed; }

@media (max-width: 720px) {
  .overlay { padding: 10px; }
  .sheet { max-height: calc(100vh - 20px); }
  .sheet > header { height: auto; min-height: 62px; padding: 12px 16px; }
  .body { grid-template-columns: minmax(0, 1fr); padding: 12px; }
  .identity { height: auto; min-height: 120px; gap: 14px; }
  .identity img, .identity-avatar { width: 76px; height: 76px; flex-basis: 76px; }
  .info dl { grid-template-columns: minmax(110px, .7fr) minmax(0, 1fr); }
}

@media (max-width: 420px) {
  .documents .document-item { grid-template-columns: 58px minmax(0, 1fr); }
  .document-preview, .document-placeholder { width: 58px; height: 52px; }
  .documents .tag { grid-column: 2; }
  .documents .document-item a { grid-column: 2; }
}
</style>
