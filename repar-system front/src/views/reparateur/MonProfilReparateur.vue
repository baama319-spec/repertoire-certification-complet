<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import LayoutReparateur from '../../layouts/LayoutReparateur.vue'
import { useAuthentification } from '../../services/serviceAuthentification'
import { api } from '../../services/api'
import { emailMessage, minLengthMessage, phoneMessage, requiredMessage } from '../../utils/formValidation'
const profil = ref({ nom: 'Awa Diop', telephone: '+221 77 000 00 00', email: 'awa.diop@reparsystem.sn', experience: '5 ans', bio: "Technicienne spécialisée avec plus de 5 ans d'expérience dans la réparation d'équipements électroniques et d'électroménager." })
const specialites = ref([]), zones = ref([]), specialitesDisponibles = ref([]), zonesDisponibles = ref([])
const localisation = ref({ latitude: null, longitude: null, statut: 'Non configurée' })
const localisationEnCours = ref(false)
const enregistre = ref(false)
const { utilisateur, mettreAJourProfil } = useAuthentification()
const photo = computed(() => utilisateur.value?.photo_profil || '')
const fichierPhoto = ref(null)
watch(utilisateur, (compte) => { if (compte) profil.value = { ...profil.value, nom: [compte.prenom, compte.nom].filter(Boolean).join(' '), telephone: compte.telephone || '', email: compte.email || '' } }, { immediate: true })
onMounted(async () => {
  try {
    const [reparateur, donneesSpecialites, donneesZones] = await Promise.all([api('/reparateurs/moi/'), api('/specialites/'), api('/localisations/')])
    specialitesDisponibles.value = donneesSpecialites.results || donneesSpecialites
    zonesDisponibles.value = donneesZones.results || donneesZones
    specialites.value = reparateur.specialites || []; zones.value = reparateur.zones_intervention || []
    profil.value = { ...profil.value, experience: reparateur.annee_experience ? `${reparateur.annee_experience} ans` : '', bio: reparateur.description || '' }
    localisation.value = { latitude: reparateur.latitude, longitude: reparateur.longitude, statut: reparateur.latitude != null && reparateur.longitude != null ? 'Position enregistrée' : 'Non configurée' }
  } catch (erreur) { window.alert(erreur.message) }
})
const sauvegarder = async () => {
  if (!utilisateur.value) return
  try {
    const erreurs = [
      requiredMessage(profil.value.nom, 'Le nom et prénom'),
      phoneMessage(profil.value.telephone),
      emailMessage(profil.value.email),
      minLengthMessage(profil.value.bio, 'La bio professionnelle', 20),
      requiredMessage(profil.value.experience, 'L’expérience'),
    ].filter(Boolean)
    if (erreurs.length) throw new Error(erreurs[0])
    const parties = profil.value.nom.trim().split(/\s+/)
    await Promise.all([mettreAJourProfil(utilisateur.value.id, JSON.stringify({ prenom: parties.shift() || '', nom: parties.join(' '), telephone: profil.value.telephone, email: profil.value.email })), api('/reparateurs/moi/', { method: 'PATCH', body: JSON.stringify({ description: profil.value.bio, annee_experience: Number.parseInt(profil.value.experience, 10) || 0, latitude: localisation.value.latitude, longitude: localisation.value.longitude, specialites: specialites.value, zones_intervention: zones.value }) })])
    enregistre.value = true; window.setTimeout(() => { enregistre.value = false }, 1800)
  } catch (erreur) { window.alert(erreur.message) }
}
const autoriserLocalisation = () => {
  if (!navigator.geolocation) { window.alert('La géolocalisation n’est pas disponible sur ce navigateur.'); return }
  localisationEnCours.value = true
  navigator.geolocation.getCurrentPosition(async ({ coords }) => {
    try {
      await api('/reparateurs/moi/', { method: 'PATCH', body: JSON.stringify({ latitude: coords.latitude, longitude: coords.longitude }) })
      localisation.value = { latitude: coords.latitude, longitude: coords.longitude, statut: 'Position enregistrée' }
    } catch (erreur) { window.alert(erreur.message) } finally { localisationEnCours.value = false }
  }, () => { localisationEnCours.value = false; window.alert('Autorisation de localisation refusée ou indisponible.') }, { enableHighAccuracy: true, timeout: 10000 })
}
const choisirPhoto = () => fichierPhoto.value?.click()
const changerPhoto = async (event) => {
  const [fichier] = event.target.files
  if (!fichier || !utilisateur.value) return
  const donnees = new FormData()
  donnees.append('photo_profil_upload', fichier)
  try { await mettreAJourProfil(utilisateur.value.id, donnees) } catch (erreur) { window.alert(erreur.message) }
  event.target.value = ''
}
const retirerZone = (zone) => { zones.value = zones.value.filter((item) => item !== zone) }
const ajouterZone = () => { const zone = zonesDisponibles.value.find(item => !zones.value.includes(item.id)); if (zone) zones.value.push(zone.id) }
const nomZone = id => { const zone = zonesDisponibles.value.find(item => item.id === id); return zone ? [zone.ville, zone.quartier || zone.nom].filter(Boolean).join(', ') : '' }
</script>
<template>
  <LayoutReparateur>
    <form class="profil-page" @submit.prevent="sauvegarder">
      <header class="profil-titre">
        <h1>Paramètres du profil professionnel</h1>
        <button class="save-button"><AppIcon name="save" :size="18"/> Enregistrer les modifications</button>
      </header>
      <div class="haut">
        <section class="bloc personnel">
          <h2><i><AppIcon name="user" :size="20"/></i> Informations personnelles &amp; compte</h2>
          <div class="corps">
            <div class="photo"><div><img :src="photo" alt="Photo de profil" /><button type="button" aria-label="Choisir une photo de profil" @click="choisirPhoto"><AppIcon name="camera" :size="15"/></button></div></div>
              <div class="nom"><input ref="fichierPhoto" class="fichier-photo" type="file" accept="image/*" @change="changerPhoto" /><label>Nom &amp; Prénom :<input v-model="profil.nom" /></label><label>Téléphone professionnel :<input v-model="profil.telephone" /></label><label>Adresse E-mail :<input v-model="profil.email" /></label></div>
          </div>
        </section>
        <section class="bloc competences">
          <h2><i><AppIcon name="wrench" :size="20"/></i> Spécialités &amp; compétences</h2>
          <div class="corps"><b>Sélectionner vos spécialités actives :</b><label v-for="item in specialitesDisponibles" :key="item.id" class="check"><input v-model="specialites" type="checkbox" :value="item.id" /><span>{{ item.nom }}</span></label><label class="experience">Années d'expérience :<select v-model="profil.experience"><option value="0">Débutant</option><option value="3 ans">3 ans</option><option value="5 ans">5 ans</option><option value="10 ans">10 ans</option></select></label><p class="verification"><AppIcon name="shield-check" :size="16"/> Statut de vérification du compte : <span><i></i>{{ utilisateur?.profil_verifie ? 'Profil vérifié' : 'En cours de vérification' }}</span></p></div>
        </section>
      </div>
      <section class="bloc zones">
        <h2><i><AppIcon name="pin" :size="20"/></i> Zones d'intervention &amp; bio</h2>
        <div class="corps">
          <div class="localisation"><b><AppIcon name="pin" :size="16"/> Ma localisation</b><p>Autoriser ReparSystem à utiliser votre position pour vous proposer aux clients proches.</p><button type="button" :disabled="localisationEnCours" @click="autoriserLocalisation">{{ localisationEnCours ? 'Récupération en cours…' : localisation.statut === 'Position enregistrée' ? 'Actualiser ma position' : 'Autoriser ma position' }}</button><small v-if="localisation.latitude != null">{{ Number(localisation.latitude).toFixed(4) }}, {{ Number(localisation.longitude).toFixed(4) }}</small></div>
          <label class="bio">Présentation / Biographie :<span><textarea v-model="profil.bio" maxlength="500"></textarea><small>{{ profil.bio.length }}/500</small></span></label>
          <div class="zone-liste"><b><AppIcon name="folder" :size="16"/> Zones d'intervention couvertes (Villes / Quartiers) :</b><section><button v-for="zone in zones" :key="zone" type="button" @click="retirerZone(zone)">{{ nomZone(zone) }} <AppIcon name="close" :size="14"/></button><button type="button" class="ajouter" :disabled="zones.length >= zonesDisponibles.length" @click="ajouterZone"><AppIcon name="plus" :size="15"/> Ajouter une zone...</button></section></div>
        </div>
      </section>
      <p v-if="enregistre" class="confirmation">Modifications enregistrées</p>
    </form>
  </LayoutReparateur>
</template>
<style scoped>
.profil-page{max-width:1332px;margin:auto;padding:12px 15px 17px;border:1px solid #e0ebf8;border-radius:10px;background:#fff;box-shadow:0 2px 10px #1647820d;color:#093578}.profil-titre{height:74px;display:flex;justify-content:space-between;align-items:flex-start;padding:4px 8px 14px;border-bottom:1px solid #e5edf8}.profil-titre>div{display:flex;gap:18px}.profil-titre>div>span{display:grid;place-items:center;width:55px;height:55px;border-radius:14px;background:#087f70;color:#fff;font-size:27px}.profil-titre h1,.bloc h2{margin:3px 0 7px;text-transform:uppercase;font-size:21px}.profil-titre p{margin:0;color:#6382af;font-size:16px}.profil-titre>button{height:46px;margin-top:4px;border:0;border-radius:8px;padding:0 19px;background:linear-gradient(135deg,#167aff,#076b64);color:#fff;font-size:12px;font-weight:700}.haut{display:grid;grid-template-columns:1.1fr 1fr;gap:15px;margin-top:16px}.bloc{border:1px solid #cfe3fb;border-radius:8px;overflow:hidden}.bloc h2{height:47px;display:flex;align-items:center;gap:15px;margin:0;padding:0 13px;background:linear-gradient(100deg,#edf8f5,#f8fbff);font-size:15px}.bloc h2 i{display:grid;place-items:center;width:33px;height:33px;border-radius:50%;background:#1074ef;color:#fff;font-style:normal;font-size:18px}.corps{padding:15px 17px}.personnel .corps{display:grid;grid-template-columns:150px 1fr;gap:13px 17px}.personnel label,.competences>.corps>b,.experience,.bio{font-size:13px;font-weight:700}.personnel label{display:grid;gap:7px}.personnel input,.experience select,.bio>span{height:39px;border:1px solid #bcd7fa;border-radius:7px;padding:0 12px;color:#103e84;font:500 13px Inter,Arial,sans-serif}.fichier-photo{display:none}.photo>b{display:block;font-size:13px}.photo>div{position:relative;width:92px;height:92px;margin-top:9px}.photo img{width:92px;height:92px;border-radius:50%;object-fit:cover}.photo button{position:absolute;right:-5px;bottom:2px;width:29px;height:29px;border:3px solid #fff;border-radius:50%;background:#0874f6;color:#fff}.nom>button{height:38px;border:1px solid #bbd8fb;border-radius:8px;background:#f7fbff;color:#0768e5;font-weight:700}.nom label{margin-top:20px}.personnel>label{grid-column:1/-1}.competences .corps{display:grid;gap:13px}.check{display:flex;align-items:center;gap:14px;font-size:14px}.check input{appearance:none;width:24px;height:24px;margin:0;border:2px solid #b7d5fc;border-radius:4px}.check input:checked{border-color:#0874f6;background:#0874f6}.check input:checked::after{content:'✓';display:block;color:#fff;text-align:center;font-size:17px}.experience{display:grid;grid-template-columns:160px 1fr;align-items:center;margin-top:6px}.verification{margin:13px 0 0;font-size:12px;font-weight:700}.verification span{display:inline-block;border-radius:18px;background:#ddf8ed;color:#09ab75;padding:8px 13px;font-weight:500}.zones{margin-top:16px}.zones .corps{padding:14px 17px 17px}.bio{display:grid;gap:7px}.bio>span{height:82px;position:relative;padding:0}.bio textarea{width:100%;height:100%;resize:none;border:0;outline:0;padding:11px;color:#31598f;font:13px Inter,Arial,sans-serif}.bio small{position:absolute;right:9px;bottom:8px;color:#6c86ad;font-size:10px}.zone-liste{margin-top:16px;font-size:12px}.zone-liste>section{display:flex;gap:12px;flex-wrap:wrap;margin:11px 0 0 32px}.zone-liste button{height:33px;border:1px solid #d3e5fb;border-radius:9px;background:#f2f8ff;color:#0968e6;padding:0 15px;font-size:12px}.zone-liste .ajouter{border-style:dashed;background:#fff}.confirmation{position:fixed;right:30px;bottom:30px;border-radius:8px;background:#0aa978;color:#fff;padding:12px 18px;font-size:13px}@media(max-width:950px){.haut{grid-template-columns:1fr}.profil-titre{height:auto;gap:15px;flex-direction:column}.personnel .corps{grid-template-columns:120px 1fr}}@media(max-width:600px){.profil-page{padding:9px}.profil-titre h1{font-size:16px}.profil-titre p{font-size:12px}.profil-titre>button{width:100%}.personnel .corps{grid-template-columns:1fr}.personnel>label{grid-column:auto}.experience{grid-template-columns:1fr}.zone-liste>section{margin-left:0}}
.localisation{margin-bottom:18px;padding:14px;border:1px solid #cfe3fb;border-radius:8px;background:#f7fbff}.localisation>b{display:block;font-size:13px;color:#174b50}.localisation p{margin:7px 0 11px;color:#6382af;font-size:11px;line-height:1.45}.localisation button{padding:9px 13px;border:0;border-radius:7px;background:#087f70;color:#fff;font-size:11px;font-weight:700}.localisation button:disabled{opacity:.65;cursor:wait}.localisation small{display:block;margin-top:9px;color:#087f70;font-size:11px;font-weight:700}
.profil-titre{align-items:center}
.profil-titre h1{margin:0;font-size:18px}
.bloc h2 i{width:24px;height:24px;border-radius:0;background:transparent;color:#087f70}
.personnel .corps{display:flex;flex-direction:column;align-items:stretch;gap:12px}
.personnel .photo{display:block}
.personnel .photo>div{margin-top:0}
.personnel .nom{display:grid;grid-template-columns:1fr;align-content:start;gap:10px;padding-top:0}
.personnel .nom label{margin-top:0}
.profil-titre .save-button{display:inline-flex;align-items:center;justify-content:center;gap:9px;background:linear-gradient(135deg,#0b9a78,#087f70)}
.profil-titre .save-button svg,.photo button svg,.bloc h2 i svg,.verification>svg,.localisation>b svg,.zone-liste>b svg,.zone-liste .ajouter svg{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.bloc h2 i svg{width:20px;height:20px}
.photo button{display:grid;place-items:center;padding:0}
.photo button svg{width:15px;height:15px}
.verification{display:flex;align-items:center;gap:8px}
.verification>svg{width:16px;height:16px;color:#0b3376}
.verification span{display:inline-flex;align-items:center;gap:8px}
.verification span i{width:7px;height:7px;border-radius:50%;background:currentColor}
.localisation>b,.zone-liste>b{display:flex;align-items:center;gap:7px}
.localisation>b svg,.zone-liste>b svg{width:16px;height:16px;color:#087f70}
.zone-liste .ajouter{display:inline-flex;align-items:center;gap:7px}
.zone-liste .ajouter svg{width:15px;height:15px}
.haut{align-items:start}
.personnel .corps{display:grid;grid-template-columns:minmax(0,1fr);grid-template-rows:92px auto;align-content:start;gap:14px;padding-top:10px}
.personnel .photo{height:92px;margin:0;padding:0;line-height:0}
.personnel .photo>div{height:92px;margin:0}
.personnel .nom{gap:16px;margin:0;padding:0}
@media(max-width:520px){.personnel .corps{gap:10px}.photo img{width:72px;height:72px}.photo>div{width:72px;height:72px}.photo button{width:25px;height:25px}.personnel .nom{gap:8px}.personnel .nom label{font-size:11px}.personnel input{padding:0 8px;font-size:11px}}
</style>
