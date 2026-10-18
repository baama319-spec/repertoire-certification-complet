import { api, apiBlob } from './api'
import { convertirAudioEnWav } from './audioWav'

export async function genererVoixAssistant (text, language = 'fr') {
  return apiBlob('/ia/voix/', {
    method: 'POST',
    body: JSON.stringify({ text, language }),
  })
}

export async function envoyerMessageAssistant (messages, langue = 'auto', photo = null) {
  if (!photo) {
    return api('/ia/assistance/', {
      method: 'POST',
      body: JSON.stringify({ messages, language: langue }),
    })
  }

  const formulaire = new FormData()
  formulaire.append('messages', JSON.stringify(messages))
  formulaire.append('language', langue)
  formulaire.append('photos', photo)
  return api('/ia/assistance/', { method: 'POST', body: formulaire })
}

export async function transcrireAudioAssistant (audio, language = 'auto') {
  const compatible = await convertirAudioEnWav(audio)
  const formulaire = new FormData()
  formulaire.append('audio', compatible, 'message.wav')
  formulaire.append('language', language)
  return api('/ia/transcription/', { method: 'POST', body: formulaire })
}