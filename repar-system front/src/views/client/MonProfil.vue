<template>
  <div class="profile-page client-profile">
    <header class="topbar">
      <RouterLink to="/" class="brand"><MarqueDashboard role="Client" tone="dark" :size="40" :text-size="17" /></RouterLink>
      <label class="search"><AppIcon name="search" :size="18"/><input placeholder="Rechercher un réparateur, une spécialité, une zone..." /></label>
      <nav><RouterLink to="/">Accueil</RouterLink><RouterLink to="/reparateurs">Trouver un réparateur</RouterLink><a>Faire un diagnostic</a><a>Devenir réparateur</a><a>À propos</a></nav>
      <div class="account"><span class="bell"><AppIcon name="bell" :size="18"/><b>3</b></span><EnteteClient /></div>
    </header>
    <main>
      <section class="profile-hero"><div class="hero-icon"><AppIcon name="user" :size="24"/></div><div><h1>Mon profil</h1><p>Gérez vos informations personnelles, vos coordonnées et la sécurité de votre compte.</p></div><aside><AppIcon name="shield" :size="15"/> Votre compte est actif <AppIcon name="check-circle" :size="15"/></aside></section>
      <section class="grid">
        <article class="card personal"><header><i><AppIcon name="user" :size="18"/></i><div><h2>Informations personnelles</h2><p>Vos informations de base et votre photo de profil.</p></div><button type="button" @click="ouvrirIdentite"><AppIcon name="pencil" :size="15"/> Modifier</button></header><div class="personal-content"><div class="photo"><div class="photo-cadre"><Avatar :photo="avatar" :nom="nomComplet" :alt="`Photo de ${nomComplet}`"/></div><span class="photo-badge"><AppIcon name="pencil" :size="13"/></span><button type="button" @click="choisirPhoto"><AppIcon name="camera" :size="15"/> Modifier la photo</button><input ref="fichierPhoto" class="fichier-photo" type="file" accept="image/jpeg,image/png,image/webp" @change="changerPhoto"><small>JPG, PNG ou WEBP · Max 5 Mo</small></div><div class="infos-personnelles"><div><span><AppIcon name="user" :size="15"/></span><p>Nom complet<b>{{ nomComplet }}</b></p></div><div><span><AppIcon name="mail" :size="15"/></span><p>Adresse e-mail<b>{{ utilisateur?.email }}</b></p></div><div><span><AppIcon name="phone" :size="15"/></span><p>Téléphone<b>{{ utilisateur?.telephone || 'Non renseigné' }}</b></p></div></div></div></article>
        <article class="card contact"><header><i><AppIcon name="pin" :size="18"/></i><div><h2>Coordonnées</h2><p>Votre zone de résidence et votre adresse principale.</p></div><button type="button" @click="ouvrirCoordonnees"><AppIcon name="pencil" :size="15"/> Modifier</button></header><div class="address"><div><span><AppIcon name="pin" :size="15"/></span><p>Zone de résidence<b>{{ libelleZone(client?.zone_residence_detail) || 'Non renseignée' }}</b></p></div><div><span><AppIcon name="home" :size="15"/></span><p>Adresse principale<b>{{ client?.adresse_principale || 'Non renseignée' }}</b></p></div><div class="map"><AppIcon name="pin" :size="18"/><b>{{ libelleZone(client?.zone_residence_detail) || 'Votre zone' }}</b></div></div></article>
      </section>
      <article class="card security"><header><i><AppIcon name="shield" :size="18"/></i><div><h2>Sécurité du compte</h2><p>Protégez votre compte avec un mot de passe sécurisé.</p></div></header><div class="password"><span><AppIcon name="shield" :size="18"/></span><p>Mot de passe<b>••••••••••••</b><small>Utilisez au moins 8 caractères.</small></p><button type="button" @click="ouvrirMotDePasse"><AppIcon name="pencil" :size="15"/> Modifier le mot de passe</button></div></article>
      <article class="danger"><i><AppIcon name="warning" :size="18"/></i><div></div><button><AppIcon name="trash" :size="15"/> Supprimer mon compte</button></article>
    </main>
    <Teleport to="body"><div v-if="modal" class="modal-backdrop" @click.self="fermerModal"><form class="modal-profil" @submit.prevent="enregistrerModal"><header><span class="modal-icon"><AppIcon :name="modal === 'identite' ? 'user' : modal === 'coordonnees' ? 'pin' : 'shield'" :size="19"/></span><div><h2>{{ modal === 'identite' ? 'Modifier mes informations' : modal === 'coordonnees' ? 'Modifier mes coordonnées' : 'Modifier le mot de passe' }}</h2><p>Vos changements seront enregistrés uniquement après confirmation.</p></div><button type="button" class="fermer" aria-label="Fermer" @click="fermerModal"><AppIcon name="close" :size="20"/></button></header><section v-if="modal === 'identite'" class="modal-champs"><label>Prénom<input v-model.trim="form.prenom" required></label><label>Nom<input v-model.trim="form.nom" required></label><label class="large">Adresse e-mail<input v-model.trim="form.email" type="email" required></label><label class="large">Téléphone<input v-model.trim="form.telephone" required></label></section><section v-else-if="modal === 'coordonnees'" class="modal-champs"><label class="large">Zone de résidence<select v-model="form.zone_residence" required><option value="" disabled>Sélectionnez votre zone</option><option v-for="zone in zones" :key="zone.id" :value="zone.id">{{ libelleZone(zone) }}</option></select></label><label class="large">Adresse principale<input v-model.trim="form.adresse_principale" placeholder="Rue, numéro, complément"></label></section><section v-else class="modal-champs"><label class="large">Mot de passe actuel<input v-model="motDePasse.actuel" type="password" required></label><label class="large">Nouveau mot de passe<input v-model="motDePasse.nouveau" type="password" minlength="8" required></label><label class="large">Confirmer le nouveau mot de passe<input v-model="motDePasse.confirmation" type="password" minlength="8" required></label></section><footer><button type="button" class="annuler" @click="fermerModal">Annuler</button><button class="enregistrer" :disabled="enregistrement">{{ enregistrement ? 'Enregistrement…' : 'Enregistrer les modifications' }}</button></footer></form></div></Teleport>
    <footer><b><LogoReparSystem :size="38"/> Repar<span>System</span></b><span>Réparez aujourd'hui, préservez demain.</span><nav><a>Aide</a><a>Confidentialité</a><a>Conditions d'utilisation</a></nav></footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EnteteClient from '../../components/client/EnteteClient.vue'
import Avatar from '../../components/commun/Avatar.vue'
import LogoReparSystem from '../../components/commun/LogoReparSystem.vue'
import MarqueDashboard from '../../components/commun/MarqueDashboard.vue'
import { useAuthentification } from '../../services/serviceAuthentification'
import { api } from '../../services/api'
import { confirmationMessage, emailMessage, passwordMessage, phoneMessage, requiredMessage } from '../../utils/formValidation'
const { utilisateur, mettreAJourProfil, changerMotDePasse } = useAuthentification()
const fichierPhoto = ref(null)
const client = ref(null), zones = ref([]), modal = ref(''), enregistrement = ref(false)
const form = ref({ prenom: '', nom: '', email: '', telephone: '', zone_residence: '', adresse_principale: '' })
const motDePasse = ref({ actuel: '', nouveau: '', confirmation: '' })
const nomComplet = computed(() => [utilisateur.value?.prenom, utilisateur.value?.nom].filter(Boolean).join(' ') || 'Mon compte')
const avatar = computed(() => utilisateur.value?.photo_profil || '')
const libelleZone = zone => zone ? [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ') : ''
const remplirFormulaire = () => { form.value = { prenom: utilisateur.value?.prenom || '', nom: utilisateur.value?.nom || '', email: utilisateur.value?.email || '', telephone: utilisateur.value?.telephone || '', zone_residence: client.value?.zone_residence || '', adresse_principale: client.value?.adresse_principale || '' } }
const ouvrirIdentite = () => { remplirFormulaire(); modal.value = 'identite' }
const ouvrirCoordonnees = () => { remplirFormulaire(); modal.value = 'coordonnees' }
const ouvrirMotDePasse = () => { motDePasse.value = { actuel: '', nouveau: '', confirmation: '' }; modal.value = 'mot_de_passe' }
const fermerModal = () => { modal.value = ''; motDePasse.value = { actuel: '', nouveau: '', confirmation: '' } }
onMounted(async () => {
  try {
    const [clients, donneesZones] = await Promise.all([api('/clients/'), api('/localisations/')])
    client.value = (clients.results || clients)[0] || null
    zones.value = donneesZones.results || donneesZones
    remplirFormulaire()
  } catch (erreur) { window.alert(erreur.message) }
})
const choisirPhoto = () => fichierPhoto.value?.click()
async function changerPhoto (event) {
  const fichier = event.target.files?.[0]
  if (!fichier || !utilisateur.value) return
  const donnees = new FormData()
  donnees.append('photo_profil_upload', fichier)
  try { await mettreAJourProfil(utilisateur.value.id, donnees) } catch (erreur) { window.alert(erreur.message) }
  event.target.value = ''
}
async function sauverIdentite () {
  const erreurs = [
    requiredMessage(form.value.prenom, 'Le prénom'),
    requiredMessage(form.value.nom, 'Le nom'),
    emailMessage(form.value.email),
    phoneMessage(form.value.telephone),
  ].filter(Boolean)
  if (erreurs.length) throw new Error(erreurs[0])
  await mettreAJourProfil(utilisateur.value.id, JSON.stringify({ prenom: form.value.prenom, nom: form.value.nom, email: form.value.email, telephone: form.value.telephone }))
}
async function sauverCoordonnees () {
  if (!client.value) return
  const erreurs = [
    requiredMessage(form.value.zone_residence, 'La zone de résidence'),
    requiredMessage(form.value.adresse_principale, 'L’adresse principale'),
  ].filter(Boolean)
  if (erreurs.length) throw new Error(erreurs[0])
  client.value = await api(`/clients/${client.value.id}/`, { method: 'PATCH', body: JSON.stringify({ zone_residence: form.value.zone_residence, adresse_principale: form.value.adresse_principale }) })
}
async function sauverMotDePasse () {
  const erreurs = [
    requiredMessage(motDePasse.value.actuel, 'Le mot de passe actuel'),
    passwordMessage(motDePasse.value.nouveau),
    confirmationMessage(motDePasse.value.nouveau, motDePasse.value.confirmation, 'La confirmation du mot de passe'),
  ].filter(Boolean)
  if (erreurs.length) throw new Error(erreurs[0])
  await changerMotDePasse({ mot_de_passe_actuel: motDePasse.value.actuel, nouveau_mot_de_passe: motDePasse.value.nouveau, confirmation_mot_de_passe: motDePasse.value.confirmation })
}
async function enregistrerModal () {
  enregistrement.value = true
  try {
    if (modal.value === 'identite') await sauverIdentite()
    else if (modal.value === 'coordonnees') await sauverCoordonnees()
    else await sauverMotDePasse()
    fermerModal()
  } catch (erreur) { window.alert(erreur.message) } finally { enregistrement.value = false }
}
</script>

<style scoped>
.profile-page{min-height:100vh;background:#f7fbff;color:#08357b}.topbar{height:75px;display:flex;align-items:center;gap:28px;padding:0 3.2%;background:#fff;border-bottom:1px solid #e6f0fc}.brand{display:flex;align-items:center;gap:12px;font-size:22px}.brand i,footer i{display:grid;place-items:center;width:43px;height:43px;border-radius:9px;background:#117bff;color:#fff;font-style:normal}.brand span,footer span{color:#087f70}.search{display:flex;align-items:center;gap:10px;width:300px;height:35px;padding:0 12px;border:1px solid #cbe0ff;border-radius:19px;color:#2976df}.search input{width:100%;border:0;outline:0;color:#2b5799;font-size:10px}.topbar nav{display:flex;gap:26px;margin:auto;font-size:10px;font-weight:700;white-space:nowrap}.account{display:flex;align-items:center;gap:13px;white-space:nowrap;font-size:11px}.bell{position:relative;font-size:20px}.bell b{position:absolute;top:-8px;right:-8px;display:grid;place-items:center;width:16px;height:16px;border-radius:50%;background:#f23754;color:#fff;font-size:8px}.available{height:33px;border:0;border-radius:18px;padding:0 13px;background:#e9fbf7;color:#093a7a;font-size:10px}.available::first-letter{color:#28c69a}.account img{width:37px;height:37px;border:2px solid #dcecff;border-radius:50%;object-fit:cover}main{max-width:1440px;margin:auto;padding:19px 3.2% 28px}.hero{display:flex;align-items:center;gap:22px;min-height:104px;padding:0 23px;border:1px solid #dceeea;border-radius:10px;background:linear-gradient(110deg,#fff,#e9f4ff)}.hero-icon,.card header>i{display:grid;place-items:center;width:70px;height:70px;border-radius:50%;background:#dbeaff;color:#117bff;font-size:34px;font-style:normal}.hero h1{margin:0 0 7px;font-size:29px}.hero p,.card header p{margin:0;color:#587ebb;font-size:13px}.hero aside{margin-left:auto;color:#4875bb;font-size:11px}.hero aside b{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;background:#55cba5;color:#fff}.grid{display:grid;grid-template-columns:1fr .94fr;gap:20px;margin-top:20px}.card{border:1px solid #dceeea;border-radius:10px;background:#fff;box-shadow:0 9px 20px #12529b08}.card>header{display:flex;align-items:center;gap:15px;padding:15px 22px}.card header>i{width:50px;height:50px;font-size:25px}.card h2{margin:0 0 6px;font-size:18px}.card header button,.password button{margin-left:auto;height:38px;padding:0 16px;border:1px solid #b9d6ff;border-radius:8px;background:#fff;color:#087f70;font-size:11px;font-weight:700}.personal-content{display:flex;gap:28px;padding:8px 23px 25px}.photo{position:relative;width:244px;min-width:210px;padding:0 14px 16px;border:1px solid #e4effb;border-radius:11px;text-align:center}.photo img{width:132px;height:132px;margin:0 auto 10px;border-radius:50%;object-fit:cover}.photo>b{position:absolute;top:105px;right:55px;display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:#087f70;color:#fff}.photo button{display:block;width:100%;height:37px;border:1px solid #b9d6ff;border-radius:7px;background:#fff;color:#087f70;font-size:11px;font-weight:700}.photo small{display:block;margin-top:9px;color:#6387bf;font-size:10px}dl{flex:1;margin:0;padding:8px 0}dl div{margin-bottom:26px}dt{color:#5278b3;font-size:11px;font-weight:700}dd{margin:10px 0 0 42px;color:#06347c;font-size:14px;font-weight:700}.address{padding:9px 23px 24px}.address>div:not(.map){display:flex;gap:22px;margin:15px 0}.address>div>span{color:#537eb9;font-size:20px}.address p{margin:0;color:#5278b3;font-size:11px;font-weight:700}.address p b{display:block;margin-top:9px;color:#06347c;font-size:14px}.map{display:flex;align-items:center;gap:14px;height:67px;margin-top:22px;padding:0 20px;border-radius:10px;background:linear-gradient(130deg,#e1f5f2,#f3f9ff 55%,#e1edf8);color:#07418f;font-size:12px}.map>span{display:grid;place-items:center;width:35px;height:35px;border-radius:50% 50% 50% 0;background:#087f70;color:#fff;transform:rotate(-45deg)}.map>a{margin-left:auto;color:#087f70;font-weight:700}.security{margin-top:18px}.security .password{display:flex;align-items:center;gap:15px;padding:7px 72px 24px}.password>span{display:grid;place-items:center;width:38px;height:38px;border-radius:50%;background:#f1f6ff;color:#537eb9}.password p{margin:0;color:#315c9e;font-size:11px;font-weight:700}.password p b,.password p small{display:block;margin-top:8px;color:#07377f;font-size:17px;letter-spacing:2px}.password p small{color:#6387bf;font-size:10px;font-weight:400;letter-spacing:0}.danger{display:flex;align-items:center;gap:18px;margin-top:24px;padding:17px 22px;border:1px solid #fde0e5;border-radius:10px;background:#fff7f7}.danger>i{display:grid;place-items:center;width:50px;height:50px;border-radius:50%;background:#ffe0e5;color:#eb1f45;font-style:normal;font-size:27px}.danger h2{margin:0 0 7px;color:#df183a;font-size:18px}.danger p{margin:0;color:#6180b6;font-size:11px}.danger button{margin-left:auto;height:38px;padding:0 17px;border:1px solid #ff9db0;border-radius:8px;background:#fff;color:#df183a;font-size:11px;font-weight:700}footer{display:flex;align-items:center;gap:17px;min-height:100px;padding:0 3.2%;border-top:1px solid #e4effb;background:#fff;color:#587ebb;font-size:11px}footer>b{display:flex;align-items:center;gap:10px;color:#07377f;font-size:15px}footer i{width:38px;height:38px;font-size:19px}footer nav{display:flex;gap:42px;margin-left:auto;color:#315e9e}@media(max-width:1100px){.search{display:none}.topbar nav{gap:14px}.grid{grid-template-columns:1fr}.personal-content{justify-content:center}}@media(max-width:700px){.topbar{gap:13px}.topbar nav,.available,.account strong{display:none}main{padding:12px}.hero{align-items:flex-start;padding:18px}.hero aside{display:none}.grid{margin-top:12px}.personal-content{flex-direction:column;align-items:center}.photo{width:90%}.security .password{padding:7px 22px 22px}.password button{padding:0 9px}.danger{align-items:flex-start}.danger button{margin:55px 0 0 -70px}footer{flex-wrap:wrap;padding:20px}footer nav{margin:0;gap:16px}}
</style>
<style scoped>.fichier-photo{display:none}</style>
<style scoped>
.personal-content{align-items:center;gap:38px;padding:18px 28px 28px}.photo{width:218px;min-width:218px;padding:20px 16px 16px;border-radius:14px;background:linear-gradient(145deg,#f9fcff,#edf6ff);box-shadow:inset 0 0 0 1px #dceeea}.photo-cadre{width:128px;height:128px;margin:0 auto 14px;padding:5px;border:2px solid #b9d8ff;border-radius:50%;background:#fff}.photo-cadre :deep(.avatar){width:100%;height:100%;font-size:28px}.photo-badge{position:absolute;top:121px;right:40px;display:grid;place-items:center;width:34px;height:34px;border:3px solid #fff;border-radius:50%;background:#087f70;color:#fff;font-size:15px}.photo button{height:40px;border-radius:9px;background:#fff;font-size:12px}.photo small{line-height:1.4}.infos-personnelles{display:grid;align-self:stretch;flex:1;min-width:0;margin:0;padding:0}.infos-personnelles>div{display:flex;align-items:flex-start;gap:22px;margin:15px 0;padding:0}.infos-personnelles>div>span{color:#537eb9;font-size:20px}.infos-personnelles p{margin:0;color:#5278b3;font-size:11px;font-weight:700}.infos-personnelles p b{display:block;margin-top:9px;color:#06347c;font-size:14px;overflow-wrap:anywhere}@media(max-width:700px){.personal-content{gap:18px}.photo{width:min(260px,100%);box-sizing:border-box}.infos-personnelles{width:100%}.photo-badge{right:calc(50% - 74px)}}
</style>
<style scoped>
.modal-backdrop{position:fixed;z-index:1000;inset:0;display:grid;place-items:center;padding:20px;background:#062b63a8;backdrop-filter:blur(5px)}.modal-profil{width:min(570px,100%);overflow:hidden;border:1px solid #cfe3ff;border-radius:18px;background:#fff;box-shadow:0 28px 80px #021b455c;color:#093578;animation:apparition .2s ease-out}.modal-profil header{display:flex;align-items:center;gap:14px;padding:22px 26px 18px;border-bottom:1px solid #e4effc;background:linear-gradient(115deg,#f7fbff,#e7f2ff)}.modal-icon{display:grid;place-items:center;width:48px;height:48px;border-radius:14px;background:#087f70;color:#fff;font-size:24px}.modal-profil h2{margin:0 0 5px;font-size:19px}.modal-profil header p{margin:0;color:#6283b4;font-size:12px}.fermer{margin-left:auto;width:34px;height:34px;border:0;border-radius:50%;background:#fff;color:#5479b1;font-size:25px;line-height:1;cursor:pointer}.fermer:hover{background:#e5f0ff;color:#087f70}.modal-champs{display:grid;grid-template-columns:1fr 1fr;gap:16px;padding:24px 26px 20px}.modal-champs label{display:grid;gap:7px;color:#315a98;font-size:12px;font-weight:700}.modal-champs .large{grid-column:1/-1}.modal-champs input,.modal-champs select{height:43px;box-sizing:border-box;width:100%;border:1px solid #bcd8fc;border-radius:9px;padding:0 12px;background:#fbfdff;color:#092f70;font:inherit;outline-color:#087f70}.modal-profil footer{display:flex;justify-content:flex-end;gap:12px;padding:17px 26px;border-top:1px solid #e4effc;background:#fbfdff}.modal-profil footer button{height:42px;border-radius:9px;padding:0 17px;font-weight:700;cursor:pointer}.annuler{border:1px solid #bcd8fc;background:#fff;color:#3970b8}.enregistrer{border:1px solid #087f70;background:#087f70;color:#fff}.enregistrer:disabled{cursor:wait;opacity:.65}@keyframes apparition{from{opacity:0;transform:translateY(12px) scale(.98)}to{opacity:1;transform:none}}@media(max-width:500px){.modal-backdrop{padding:12px}.modal-profil header,.modal-champs,.modal-profil footer{padding-left:17px;padding-right:17px}.modal-champs{grid-template-columns:1fr}.modal-champs .large{grid-column:auto}.modal-profil footer button{flex:1;padding:0 8px}}
</style>
<style scoped>
.client-profile{width:100%!important;margin:0!important;padding:0!important;background:#f7fbff!important}
.client-profile .topbar{width:100%!important}
.client-profile>main{max-width:1536px!important;margin:0 auto!important;padding:19px 3.2% 28px!important}
.client-profile>footer{width:100%!important}
.profile-page .profile-hero{display:flex!important;align-items:center!important;gap:22px!important;height:104px!important;min-height:104px!important;box-sizing:border-box!important;overflow:hidden!important;padding:0 23px!important;border:1px solid #dceeea!important;border-radius:10px!important;background:linear-gradient(110deg,#fff,#e9f4ff)!important}
.profile-page .profile-hero h1{margin:0 0 7px!important;color:#08357b!important;font-size:29px!important;line-height:1.1!important}
.profile-page .profile-hero p{margin:0!important;color:#587ebb!important;font-size:13px!important}
.profile-page .profile-hero aside{margin-left:auto!important;color:#4875bb!important;font-size:11px!important}
.client-profile .personal-content{padding-bottom:32px!important}
.client-profile .photo{padding-top:7px!important;padding-bottom:0!important}
.client-profile .photo img{width:124px!important;height:124px!important}
.client-profile .photo>b{top:99px!important}
.client-profile .address .map{height:85px!important;margin-top:37px!important}
.client-profile .security .password{padding-bottom:30px!important}
.client-profile .security{margin-top:22px!important}
.client-profile .danger{padding-top:25px!important;padding-bottom:25px!important}
.client-profile .danger{margin-top:-7px!important}
</style>
