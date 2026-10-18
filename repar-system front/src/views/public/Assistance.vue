<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import EntetePublic from '../../components/public/EntetePublic.vue'
import { envoyerMessageAssistant, genererVoixAssistant, transcrireAudioAssistant } from '../../services/serviceAssistant'

const langue = ref('auto')
const brouillon = ref('')
const urlsPhotos = new Set()
const messages = ref([{
  role: 'assistant',
  content: 'Bonjour ! Je suis l’assistant de ReparSystem. Quel appareil souhaitez-vous faire réparer ?',
  heure: heureActuelle(),
}])
const envoiEnCours = ref(false)
const erreur = ref('')
const erreurVoix = ref('')
const voixActive = ref(false)
const voixEnPreparation = ref(false)
const voixEnCours = ref(false)
const photo = ref(null)
const apercuPhoto = ref('')
const enregistrementEnCours = ref(false)
const transcriptionEnCours = ref(false)
const microActif = ref(false)
const dureeEnregistrement = ref(0)
const zoneMessages = ref(null)
const zoneTexte = ref(null)
let enregistreurAudio = null
let fluxAudio = null
let lecteurAudio = null
let urlAudio = ''
let numeroLecture = 0
let debutEnregistrement = 0
let minuterieMicro = null

const libelleLangue = computed(() => ({ auto: 'Automatique', fr: 'Français', wo: 'Wolof' })[langue.value])

function heureActuelle () {
  return new Intl.DateTimeFormat('fr-FR', { hour: '2-digit', minute: '2-digit' }).format(new Date())
}

const defilerVersBas = async () => {
  await nextTick()
  if (zoneMessages.value) zoneMessages.value.scrollTop = zoneMessages.value.scrollHeight
}

watch(messages, defilerVersBas, { deep: true })

const parlerAvecVoixNative = (texte, numero) => {
  if (!('speechSynthesis' in window)) return
  window.speechSynthesis.cancel()
  const parole = new SpeechSynthesisUtterance(texte)
  parole.onstart = () => {
    if (numero === numeroLecture) {
      voixEnPreparation.value = false
      voixEnCours.value = true
    }
  }
  parole.onend = parole.onerror = () => {
    if (numero === numeroLecture) {
      voixEnPreparation.value = false
      voixEnCours.value = false
    }
  }
  const langueParole = langue.value === 'wo' ? 'wo-SN' : 'fr-FR'
  parole.lang = langueParole
  const voix = window.speechSynthesis.getVoices()
  const voixChoisie = voix.find((element) => element.lang.toLowerCase().startsWith(langueParole.toLowerCase()))
    || (langue.value === 'auto' ? voix.find((element) => element.lang.toLowerCase().startsWith('wo')) : null)
  if (voixChoisie) parole.voice = voixChoisie
  window.speechSynthesis.speak(parole)
}

const parler = async (texte) => {
  const numero = ++numeroLecture
  erreurVoix.value = ''
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
  lecteurAudio?.pause()
  if (urlAudio) URL.revokeObjectURL(urlAudio)
  voixEnCours.value = false
  voixEnPreparation.value = true
  try {
    const audio = await genererVoixAssistant(texte, langue.value === 'wo' ? 'wo' : 'fr')
    if (numero !== numeroLecture) return
    urlAudio = URL.createObjectURL(audio)
    lecteurAudio = new Audio(urlAudio)
    lecteurAudio.onended = () => {
      if (numero === numeroLecture) voixEnCours.value = false
    }
    lecteurAudio.onerror = () => {
      if (numero === numeroLecture) voixEnCours.value = false
    }
    await lecteurAudio.play()
    voixEnPreparation.value = false
    voixEnCours.value = true
  } catch (cause) {
    if (numero !== numeroLecture) return
    // La synthèse native permet de continuer si Soynade est indisponible.
    erreurVoix.value = `${cause.message || 'La lecture Edge TTS a échoué.'} La voix du navigateur prend le relais.`
    parlerAvecVoixNative(texte, numero)
  }
}

const arreterLecture = () => {
  numeroLecture += 1
  lecteurAudio?.pause()
  lecteurAudio = null
  if (urlAudio) URL.revokeObjectURL(urlAudio)
  urlAudio = ''
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
  voixEnPreparation.value = false
  voixEnCours.value = false
}

const basculerVoix = () => {
  voixActive.value = !voixActive.value
  if (!voixActive.value) {
    arreterLecture()
    return
  }
  const derniereReponse = [...messages.value].reverse().find((message) => message.role === 'assistant')
  if (derniereReponse) parler(derniereReponse.content)
}

const rejouer = (texte) => {
  voixActive.value = true
  parler(texte)
}

const envoyer = async () => {
  const texte = brouillon.value.trim()
  if ((!texte && !photo.value) || envoiEnCours.value) return
  erreur.value = ''
  const texteEnvoye = texte || 'Pouvez-vous regarder cette photo et me dire ce que vous observez ?'
  const photoEnvoyee = photo.value
  const historique = [...messages.value, { role: 'user', content: texteEnvoye }]
  messages.value.push({ role: 'user', content: texteEnvoye, heure: heureActuelle(), image: apercuPhoto.value || '' })
  brouillon.value = ''
  photo.value = null
  apercuPhoto.value = ''
  envoiEnCours.value = true
  try {
    const resultat = await envoyerMessageAssistant(
      historique.slice(-12).map(({ role, content }) => ({ role, content })),
      langue.value,
      photoEnvoyee,
    )
    messages.value.push({ role: 'assistant', content: resultat.reply, heure: heureActuelle() })
    if (voixActive.value) parler(resultat.reply)
  } catch (cause) {
    erreur.value = cause.message || 'Impossible de joindre l’assistant. Réessayez.'
  } finally {
    envoiEnCours.value = false
    await nextTick()
    zoneTexte.value?.focus()
  }
}

const choisirPhoto = (event) => {
  const fichier = event.target.files?.[0]
  event.target.value = ''
  if (!fichier) return
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(fichier.type)) {
    erreur.value = 'Choisissez une image JPG, PNG ou WEBP.'
    return
  }
  if (fichier.size > 5 * 1024 * 1024) {
    erreur.value = 'La photo doit faire 5 Mo maximum.'
    return
  }
  if (apercuPhoto.value) {
    URL.revokeObjectURL(apercuPhoto.value)
    urlsPhotos.delete(apercuPhoto.value)
  }
  photo.value = fichier
  apercuPhoto.value = URL.createObjectURL(fichier)
  urlsPhotos.add(apercuPhoto.value)
  erreur.value = ''
}

const retirerPhoto = () => {
  if (apercuPhoto.value) {
    URL.revokeObjectURL(apercuPhoto.value)
    urlsPhotos.delete(apercuPhoto.value)
  }
  photo.value = null
  apercuPhoto.value = ''
}

const demarrerMicro = async () => {
  erreur.value = ''
  dureeEnregistrement.value = 0
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    erreur.value = 'Le microphone n’est pas pris en charge par ce navigateur.'
    return
  }
  try {
    fluxAudio = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } })
    const mimeType = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus'].find((format) => MediaRecorder.isTypeSupported(format))
    enregistreurAudio = new MediaRecorder(fluxAudio, mimeType ? { mimeType, audioBitsPerSecond: 64000 } : { audioBitsPerSecond: 64000 })
    const morceaux = []
    enregistreurAudio.ondataavailable = (event) => { if (event.data.size) morceaux.push(event.data) }
    enregistreurAudio.onstop = async () => {
      if (minuterieMicro) window.clearInterval(minuterieMicro)
      minuterieMicro = null
      fluxAudio?.getTracks().forEach((piste) => piste.stop())
      fluxAudio = null
      microActif.value = false
      const enregistreurTermine = enregistreurAudio
      const audio = new Blob(morceaux, { type: enregistreurTermine?.mimeType || 'audio/webm' })
      if (!audio.size) {
        erreur.value = 'Aucun son n’a été enregistré. Autorisez le microphone et vérifiez qu’il fonctionne.'
        return
      }
      if (dureeEnregistrement.value < 1) {
        erreur.value = 'Enregistrement trop court. Appuyez sur le micro, parlez, puis appuyez de nouveau pour arrêter.'
        return
      }
      transcriptionEnCours.value = true
      try {
        const resultat = await transcrireAudioAssistant(audio, langue.value)
        const texteTranscrit = resultat.text?.trim()
        if (!texteTranscrit) {
          erreur.value = 'Aucune parole claire reconnue. Vérifiez le micro, parlez après son démarrage et arrêtez-le après votre phrase.'
          return
        }
        brouillon.value = [brouillon.value.trim(), texteTranscrit].filter(Boolean).join(' ')
        zoneTexte.value?.focus()
      } catch (cause) {
        erreur.value = cause.message || 'La transcription a échoué. Réessayez.'
      } finally {
        transcriptionEnCours.value = false
      }
    }
    enregistreurAudio.start(250)
    microActif.value = true
    enregistrementEnCours.value = true
    debutEnregistrement = Date.now()
    minuterieMicro = window.setInterval(() => {
      dureeEnregistrement.value = Math.floor((Date.now() - debutEnregistrement) / 1000)
      if (dureeEnregistrement.value >= 90) arreterMicro()
    }, 250)
  } catch (cause) {
    fluxAudio?.getTracks().forEach((piste) => piste.stop())
    fluxAudio = null
    erreur.value = cause.name === 'NotAllowedError'
      ? 'Autorisez l’accès au microphone dans votre navigateur.'
      : 'Impossible de démarrer le microphone.'
  }
}

const arreterMicro = () => {
  enregistrementEnCours.value = false
  if (minuterieMicro) window.clearInterval(minuterieMicro)
  minuterieMicro = null
  if (enregistreurAudio && enregistreurAudio.state !== 'inactive') enregistreurAudio.stop()
}

const basculerMicro = () => {
  if (microActif.value) arreterMicro()
  else demarrerMicro()
}

const nouvelleConversation = () => {
  arreterLecture()
  messages.value = [{
    role: 'assistant',
    content: 'Bonjour ! Je suis l’assistant de ReparSystem. Quel appareil souhaitez-vous faire réparer ?',
    heure: heureActuelle(),
  }]
  erreur.value = ''
}

onBeforeUnmount(() => {
  arreterLecture()
  if (minuterieMicro) window.clearInterval(minuterieMicro)
  if (enregistreurAudio && enregistreurAudio.state !== 'inactive') enregistreurAudio.stop()
  fluxAudio?.getTracks().forEach((piste) => piste.stop())
  urlsPhotos.forEach((url) => URL.revokeObjectURL(url))
})
</script>

<template>
  <EntetePublic />
  <main class="assistant-page">
    <section class="assistant-showcase" aria-label="Assistant ReparSystem">
      <header class="showcase-brand">
        <RouterLink class="back-home" to="/" aria-label="Retour à l’accueil">‹</RouterLink>
        <span class="brand-mark">R</span>
        <span>ReparSystem</span>
      </header>
      <div class="showcase-content">
        <span class="eyebrow">VOTRE ASSISTANT DE RÉPARATION</span>
        <h1>On trouve ensemble la panne.</h1>
        <p class="showcase-intro">Expliquez ce qui se passe, en français ou en wolof. Je suis là pour vous guider.</p>
        <div class="robot-stage" :class="{ listening: microActif }">
          <div class="robot-halo"></div>
          <div class="speech-bubble">Bonjour ! Quel appareil souhaitez-vous faire réparer ?</div>
          <div class="sound-lines sound-left"><i></i><i></i><i></i><i></i></div>
          <div class="sound-lines sound-right"><i></i><i></i><i></i><i></i></div>
          <svg class="robot" viewBox="0 0 300 350" role="img" aria-label="Petit robot vert ReparSystem">
            <defs>
              <linearGradient id="shell" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#fff"/><stop offset=".58" stop-color="#e9f2ef"/><stop offset="1" stop-color="#c8ddd7"/></linearGradient>
              <linearGradient id="green" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#4cc7a5"/><stop offset="1" stop-color="#087f70"/></linearGradient>
              <radialGradient id="face"><stop stop-color="#173d3a"/><stop offset="1" stop-color="#092b30"/></radialGradient>
            </defs>
            <path d="M150 42V18" stroke="#087f70" stroke-width="11" stroke-linecap="round"/><circle cx="150" cy="14" r="13" fill="url(#green)"/>
            <path d="M70 170 35 192v48l35 16m160-86 35 22v48l-35 16" fill="none" stroke="#0a806f" stroke-width="19" stroke-linecap="round" stroke-linejoin="round"/>
            <rect x="39" y="198" width="22" height="39" rx="11" fill="url(#green)"/><rect x="239" y="198" width="22" height="39" rx="11" fill="url(#green)"/>
            <path d="M78 278c0-24 19-43 43-43h58c24 0 43 19 43 43v59H78z" fill="url(#shell)" stroke="#b6d2cb" stroke-width="4"/>
            <path d="M115 255c-4 23-21 34-39 35l-15 36h30l28-29m66-42c4 23 21 34 39 35l15 36h-30l-28-29" fill="url(#green)" stroke="#087f70" stroke-width="4" stroke-linejoin="round"/>
            <path d="M131 249h38v18c0 10-8 18-19 18s-19-8-19-18z" fill="#173b3b"/>
            <rect x="46" y="77" width="208" height="167" rx="76" fill="url(#shell)" stroke="#b8d4ce" stroke-width="5"/>
            <rect x="62" y="93" width="176" height="133" rx="61" fill="url(#face)"/>
            <path d="M102 121c9-9 18-11 27-7m42 0c10-6 20-4 28 4" fill="none" stroke="#28bd91" stroke-width="8" stroke-linecap="round"/>
            <ellipse cx="116" cy="158" rx="17" ry="22" fill="#e7fffa"/><ellipse cx="184" cy="158" rx="17" ry="22" fill="#e7fffa"/>
            <ellipse cx="119" cy="162" rx="9" ry="14" fill="#0e8272"/><ellipse cx="181" cy="162" rx="9" ry="14" fill="#0e8272"/>
            <circle cx="122" cy="155" r="4" fill="#fff"/><circle cx="184" cy="155" r="4" fill="#fff"/>
            <path d="M119 190c18 23 47 23 64 0" fill="none" stroke="#f4fffb" stroke-width="8" stroke-linecap="round"/>
            <path d="M135 201c10 8 23 8 32 0-2 14-11 19-17 19s-14-5-15-19" fill="#f48372"/>
            <path d="M83 106c-13 21-15 54-7 84m148-84c13 21 15 54 7 84" fill="none" stroke="#fff" stroke-width="5" opacity=".65" stroke-linecap="round"/>
            <path d="M142 296h17l-10 13h11l-20 19 5-15h-11z" fill="#118876"/>
          </svg>
        </div>
        <div class="voice-cta">
          <button class="big-mic" :class="{ active: microActif }" :disabled="transcriptionEnCours" type="button" :aria-label="microActif ? 'Arrêter le microphone' : 'Parler à l’assistant'" @click="basculerMicro">
            <svg v-if="!transcriptionEnCours" viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0m-7 7v3m-4 0h8"/></svg>
            <span v-else class="loader"></span>
          </button>
          <strong>{{ microActif ? `Je vous écoute… ${dureeEnregistrement}s · appuyez pour arrêter` : transcriptionEnCours ? 'Je transcris votre message…' : 'Appuyez pour parler' }}</strong>
          <div class="waveform" :class="{ moving: microActif }" aria-hidden="true"><i v-for="bar in 29" :key="bar"></i></div>
          <p>Français · Wolof</p>
        </div>
      </div>
      <footer class="showcase-footer"><span><span class="safe-dot"></span> Conseils clairs, sans jargon</span><span>Votre assistant, à votre écoute</span></footer>
    </section>

    <section class="chat-panel" aria-label="Conversation avec l’assistant">
      <header class="chat-header">
        <div class="bot-avatar"><span>R</span><i></i></div>
        <div class="chat-title"><strong>Assistant ReparSystem</strong><span><i></i> {{ voixEnPreparation ? 'Préparation de la voix…' : voixEnCours ? 'L’assistant parle…' : 'En conversation' }}</span></div>
        <button class="voice-toggle" :aria-pressed="voixActive" type="button" @click="basculerVoix">{{ voixActive ? 'Désactiver la voix' : 'Activer la voix' }}</button>
        <button v-if="voixEnCours || voixEnPreparation" class="stop-voice" type="button" @click="arreterLecture">Arrêter</button>
        <button class="new-chat" type="button" title="Nouvelle conversation" aria-label="Nouvelle conversation" @click="nouvelleConversation">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14m-7-7h14"/></svg>
        </button>
      </header>

      <div ref="zoneMessages" class="messages" aria-live="polite">
        <article v-for="(message, index) in messages" :key="`${index}-${message.heure}`" class="message-row" :class="message.role">
          <div v-if="message.role === 'assistant'" class="small-avatar">R</div>
          <div class="message-content">
            <div class="bubble" :class="message.role"><p>{{ message.content }}</p><img v-if="message.image" :src="message.image" alt="Photo envoyée pour le diagnostic"><button v-if="message.role === 'assistant'" class="speak-message" type="button" title="Écouter la réponse" aria-label="Écouter la réponse" @click="rejouer(message.content)"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7m3-10a9 9 0 0 1 0 13"/></svg></button></div>
            <time>{{ message.heure }}</time>
          </div>
          <div v-if="message.role === 'user'" class="user-avatar">Vous</div>
        </article>
        <article v-if="envoiEnCours" class="message-row assistant"><div class="small-avatar">R</div><div class="bubble assistant typing"><i></i><i></i><i></i><span>L’assistant réfléchit…</span></div></article>
      </div>

      <div class="chat-bottom">
        <p v-if="erreur" class="chat-error" role="alert">{{ erreur }}</p>
        <p v-if="erreurVoix" class="chat-error" role="status">{{ erreurVoix }}</p>
        <div v-if="apercuPhoto" class="photo-preview"><img :src="apercuPhoto" alt="Aperçu de la photo à envoyer"><span>{{ photo?.name }}</span><button type="button" aria-label="Retirer la photo" @click="retirerPhoto">×</button></div>
        <form class="composer" @submit.prevent="envoyer">
          <textarea ref="zoneTexte" v-model="brouillon" rows="1" maxlength="3000" :disabled="envoiEnCours" :placeholder="transcriptionEnCours ? 'Transcription en cours…' : microActif ? `Parlez maintenant… ${dureeEnregistrement}s (appuyez pour arrêter)` : 'Tapez ou appuyez sur le micro pour parler…'" @keydown.enter.exact.prevent="envoyer"></textarea>
          <button class="composer-mic" :class="{ active: microActif }" type="button" :disabled="transcriptionEnCours" :aria-label="microActif ? 'Arrêter le microphone' : 'Dicter un message'" @click="basculerMicro"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0m-7 7v3m-4 0h8"/></svg></button>
          <button class="send-button" type="submit" :disabled="envoiEnCours || (!brouillon.trim() && !photo)" aria-label="Envoyer le message"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 14-7-4 14-3-6zM12 13l7-8"/></svg></button>
        </form>
        <div class="chat-actions">
          <label class="photo-button"><input type="file" accept="image/jpeg,image/png,image/webp" @change="choisirPhoto"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="8.5" cy="10" r="1.5"/><path d="m21 15-5-5L5 19"/></svg>Ajouter une photo</label>
          <label class="language-button"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18m-9-9a15 15 0 0 1 0 18m0-18a15 15 0 0 0 0 18"/></svg><span>Langue</span><select v-model="langue" :aria-label="`Langue de l’assistant : ${libelleLangue}`"><option value="auto">Auto</option><option value="fr">Français</option><option value="wo">Wolof</option></select></label>
        </div>
        <p class="voice-note">Voix Soynade · Français/Wolof. Activez-la une première fois pour autoriser la lecture automatique. Les messages restent visibles ici.</p>
      </div>
    </section>
  </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
*{box-sizing:border-box}
.assistant-page{height:calc(100vh - 70px);height:calc(100dvh - 70px);min-height:0;display:grid;grid-template-columns:minmax(340px,.95fr) minmax(420px,1.05fr);gap:16px;padding:12px;background:#f2f7f5;color:#143943;font-family:'DM Sans',sans-serif;overflow:hidden}
.assistant-showcase,.chat-panel{height:100%;min-height:0;border:1px solid #dcebe6;border-radius:19px;background:#fff;overflow:hidden}
.assistant-showcase{position:relative;display:flex;flex-direction:column;padding:24px clamp(24px,4vw,58px) 20px;background:radial-gradient(ellipse at 52% 48%,#e1f4ec 0%,#f5fbf8 49%,#fff 88%)}
.showcase-brand{display:flex;align-items:center;gap:10px;color:#103b3c;font-weight:800;font-size:16px}.back-home{display:grid;place-items:center;width:34px;height:34px;margin-right:2px;border:1px solid #cce3dc;border-radius:50%;color:#087f70;font-size:24px;line-height:1}.brand-mark,.bot-avatar,.small-avatar{display:grid;place-items:center;background:linear-gradient(145deg,#48c5a0,#087b6e);color:#fff;font-family:Manrope,sans-serif;font-weight:800}.brand-mark{width:33px;height:33px;border-radius:50%;box-shadow:0 4px 12px #087f7033}
.showcase-content{display:flex;min-height:0;flex:1;flex-direction:column;align-items:center;justify-content:center;padding-top:16px;text-align:center}.eyebrow{color:#178773;font-size:10px;font-weight:800;letter-spacing:1.7px}.showcase-content h1{max-width:390px;margin:12px 0 8px;color:#102f37;font:800 clamp(28px,3.3vw,42px)/1.13 Manrope,sans-serif;letter-spacing:-1.4px}.showcase-intro{max-width:370px;margin:0;color:#60797a;font-size:14px;line-height:1.6}
.robot-stage{position:relative;display:grid;width:min(100%,405px);height:min(43vh,385px);min-height:285px;place-items:center;margin:8px 0 3px}.robot-halo{position:absolute;width:78%;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#d5f1e5 0%,#e5f6ef 65%,transparent 66%)}.robot{position:absolute;bottom:0;width:min(70%,280px);height:94%;overflow:visible;filter:drop-shadow(0 16px 16px #0a62422a);animation:float 4s ease-in-out infinite}.speech-bubble{position:absolute;z-index:1;top:-4%;right:0;max-width:205px;padding:13px 16px;border:1px solid #bce4d8;border-radius:17px;background:#ffffffed;color:#143943;text-align:left;font-size:12px;line-height:1.55;box-shadow:0 7px 18px #096c5214}.speech-bubble:after{position:absolute;bottom:-8px;left:20px;width:14px;height:14px;border-right:1px solid #bce4d8;border-bottom:1px solid #bce4d8;background:#fff;content:'';transform:rotate(45deg)}.sound-lines{position:absolute;z-index:1;top:51%;display:flex;align-items:center;gap:5px;height:45px}.sound-left{left:0}.sound-right{right:0}.sound-lines i{width:5px;height:25%;border-radius:8px;background:#a4dfd0}.sound-lines i:nth-child(2){height:60%}.sound-lines i:nth-child(3){height:95%}.sound-lines i:nth-child(4){height:45%}
.voice-cta{display:flex;flex-direction:column;align-items:center;gap:9px}.big-mic{display:grid;width:76px;height:76px;place-items:center;border:7px solid #d7f0e9;border-radius:50%;background:linear-gradient(145deg,#20a78b,#087f70);color:#fff;box-shadow:0 8px 24px #087f7030;cursor:pointer;transition:.2s}.big-mic:hover,.big-mic.active{transform:scale(1.04);box-shadow:0 0 0 8px #c3eadf}.big-mic.active{background:linear-gradient(145deg,#dc6470,#b83144)}.big-mic svg{width:27px;height:27px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}.big-mic:disabled{cursor:wait}.voice-cta strong{color:#20504c;font-size:12px}.voice-cta p{margin:-2px 0 0;color:#7a9692;font-size:10px}.waveform{display:flex;align-items:center;justify-content:center;gap:3px;height:23px}.waveform i{width:3px;height:8px;border-radius:4px;background:#14967c}.waveform i:nth-child(3n){height:15px}.waveform i:nth-child(5n){height:20px}.waveform.moving i{animation:wave .7s ease-in-out infinite alternate}.waveform.moving i:nth-child(2n){animation-delay:.3s}.waveform.moving i:nth-child(3n){animation-delay:.5s}.showcase-footer{display:flex;justify-content:space-between;gap:10px;padding-top:16px;color:#74908d;font-size:10px}.showcase-footer span:first-child{display:flex;align-items:center;gap:7px}.safe-dot,.chat-title span i{display:inline-block;width:7px;height:7px;border-radius:50%;background:#37bd77}
.chat-panel{display:flex;flex-direction:column;background:linear-gradient(180deg,#fff 0%,#fcfefe 100%)}.chat-header{display:flex;align-items:center;gap:12px;padding:19px 22px;border-bottom:1px solid #edf3f1}.bot-avatar{position:relative;width:39px;height:39px;border:3px solid #e1f1eb;border-radius:50%;font-size:13px}.bot-avatar i{position:absolute;right:-1px;bottom:0;width:9px;height:9px;border:2px solid white;border-radius:50%;background:#35c571}.chat-title{display:flex;flex:1;flex-direction:column;gap:4px}.chat-title strong{color:#153d42;font:700 14px Manrope,sans-serif}.chat-title span{display:flex;align-items:center;gap:6px;color:#188671;font-size:10px}.chat-title span i{width:6px;height:6px}.new-chat{display:grid;width:35px;height:35px;place-items:center;border:1px solid #e1ece8;border-radius:10px;background:#fff;color:#53827b;cursor:pointer}.new-chat:hover{background:#f0faf6}.new-chat svg{width:17px;height:17px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}
.messages{display:flex;flex:1;flex-direction:column;gap:18px;min-height:0;padding:22px clamp(15px,3vw,28px);overflow-y:auto;overflow-x:hidden;scroll-behavior:smooth;scrollbar-width:none;-ms-overflow-style:none}.messages::-webkit-scrollbar{display:none}.message-row{display:flex;align-items:flex-start;gap:9px}.message-row.user{justify-content:flex-end}.small-avatar{flex:none;width:28px;height:28px;margin-top:3px;border:2px solid #e4f2ed;border-radius:50%;font-size:10px}.message-content{display:flex;max-width:min(83%,390px);flex-direction:column;gap:5px}.bubble{position:relative;padding:12px 13px;border-radius:15px 15px 15px 5px;background:linear-gradient(135deg,#eff8f4,#eaf6f4);color:#173b43;font-size:12px;line-height:1.6}.bubble p{margin:0;white-space:pre-wrap;overflow-wrap:anywhere}.bubble.user{border-radius:15px 15px 5px 15px;background:#eef5fb;color:#173d55}.bubble img{display:block;width:min(100%,220px);max-height:150px;margin-top:9px;border-radius:9px;object-fit:cover}.message-content time{padding:0 5px;color:#82999a;font-size:9px}.message-row.user .message-content time{text-align:right}.user-avatar{display:grid;flex:none;width:29px;height:29px;place-items:center;margin-top:2px;border-radius:50%;background:#e6edf2;color:#47616c;font-size:8px;font-weight:700}.speak-message{position:absolute;right:8px;bottom:7px;display:grid;width:23px;height:23px;place-items:center;border:0;border-radius:50%;background:#ffffff9c;color:#177f71;cursor:pointer}.speak-message svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.bubble.assistant:has(.speak-message){padding-right:38px}.typing{display:flex;align-items:center;gap:4px;min-height:39px}.typing i{width:5px;height:5px;border-radius:50%;background:#14967c;animation:dot .8s infinite alternate}.typing i:nth-child(2){animation-delay:.2s}.typing i:nth-child(3){animation-delay:.4s}.typing span{margin-left:5px;color:#718a87;font-size:10px}
.chat-bottom{padding:0 18px 16px}.chat-error{margin:0 0 9px;padding:9px 12px;border:1px solid #f4d3d2;border-radius:9px;background:#fff5f4;color:#a23e3f;font-size:11px}.composer{display:flex;align-items:center;gap:5px;min-height:48px;padding:5px 7px 5px 14px;border:1px solid #d6e6e1;border-radius:17px;background:#fff;box-shadow:0 4px 14px #153d4208}.composer:focus-within{border-color:#7dc9b8;box-shadow:0 0 0 3px #dff4ed}.composer textarea{flex:1;max-height:90px;resize:none;border:0;outline:0;background:transparent;color:#173b43;font:400 12px/1.45 'DM Sans',sans-serif}.composer textarea::placeholder{color:#8da2a5}.composer-mic,.send-button{display:grid;flex:none;width:32px;height:32px;place-items:center;border:0;border-radius:50%;background:transparent;color:#168777;cursor:pointer}.composer-mic.active{background:#fff0f0;color:#c94450}.composer-mic:disabled{opacity:.5}.composer-mic svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.send-button{background:#118776;color:#fff}.send-button:disabled{opacity:.4;cursor:not-allowed}.send-button svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.chat-actions{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:12px}.photo-button,.language-button{display:inline-flex;position:relative;align-items:center;gap:7px;min-height:34px;padding:0 11px;border:1px solid #d9e8e3;border-radius:999px;background:#fff;color:#4d7476;font-size:10px;white-space:nowrap}.photo-button{color:#138571;cursor:pointer}.photo-button:hover,.language-button:hover{border-color:#a4d5c8;background:#f6fbf8}.photo-button input{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:pointer}.photo-button svg,.language-button svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.language-button{gap:6px;padding-right:5px}.language-button select{border:0;outline:0;background:transparent;color:#42696b;font:inherit;cursor:pointer}.voice-note{margin:10px 0 0;color:#93a6a5;font-size:9px;line-height:1.4;text-align:center}.photo-preview{display:flex;align-items:center;gap:9px;margin:0 0 9px;padding:5px 8px;border:1px solid #e0ede8;border-radius:10px;color:#587574;font-size:10px}.photo-preview img{width:34px;height:34px;border-radius:6px;object-fit:cover}.photo-preview span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.photo-preview button{border:0;background:none;color:#9a6666;font-size:17px;cursor:pointer}.loader{width:19px;height:19px;border:2px solid #fff8;border-top-color:#fff;border-radius:50%;animation:spin .8s linear infinite}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}@keyframes wave{from{transform:scaleY(.55)}to{transform:scaleY(1.4)}}@keyframes dot{to{opacity:.3;transform:translateY(-3px)}}@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:860px){.assistant-page{grid-template-columns:minmax(250px,.75fr) minmax(0,1.25fr);gap:10px;padding:8px}.assistant-showcase{padding:18px}.showcase-intro{font-size:12px}.robot-stage{height:min(34vh,300px);min-height:0;flex:1}.speech-bubble{max-width:165px;font-size:10px}.sound-lines{transform:scale(.75)}}
@media(max-width:800px){.assistant-page{height:calc(100vh - 62px);height:calc(100dvh - 62px)}}
@media(max-width:640px){.assistant-page{display:flex;flex-direction:column;padding:0;background:#fff}.assistant-showcase{display:none}.chat-panel{height:100%;min-height:0;border:0;border-radius:0}.chat-header{flex:none;padding:13px 16px}.messages{gap:14px;padding:17px 14px}.chat-bottom{flex:none;padding:0 12px max(12px,env(safe-area-inset-bottom))}.message-content{max-width:86%}.voice-note{font-size:8px}}
</style>

<style scoped>
.voice-toggle,
.stop-voice {
  min-height: 34px;
  padding: 0 11px;
  border: 1px solid #cde5dc;
  border-radius: 999px;
  background: #f4fbf8;
  color: #147967;
  font: inherit;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}
.voice-toggle[aria-pressed="true"] { background: #e6f6ef; border-color: #91cfba; }
.stop-voice { color: #a43b46; background: #fff5f4; border-color: #f0d1ce; }
.voice-toggle:hover, .stop-voice:hover { filter: brightness(.97); }
@media (max-width: 640px) {
  .voice-toggle, .stop-voice { min-height: 31px; padding: 0 8px; font-size: 9px; }
}
</style>