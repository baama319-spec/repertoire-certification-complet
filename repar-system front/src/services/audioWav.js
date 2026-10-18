export async function convertirAudioEnWav (audio) {
  if (audio.type === 'audio/wav' || audio.type === 'audio/x-wav') return audio

  const ContexteAudio = window.AudioContext || window.webkitAudioContext
  if (!ContexteAudio) throw new Error('Ce navigateur ne peut pas convertir l’enregistrement pour la transcription.')

  const contexte = new ContexteAudio()
  try {
    const bufferAudio = await contexte.decodeAudioData(await audio.arrayBuffer())
    const nombreEchantillons = bufferAudio.length
    const wav = new ArrayBuffer(44 + nombreEchantillons * 2)
    const vue = new DataView(wav)
    const ecrireTexte = (offset, texte) => {
      for (let index = 0; index < texte.length; index += 1) vue.setUint8(offset + index, texte.charCodeAt(index))
    }

    ecrireTexte(0, 'RIFF')
    vue.setUint32(4, 36 + nombreEchantillons * 2, true)
    ecrireTexte(8, 'WAVE')
    ecrireTexte(12, 'fmt ')
    vue.setUint32(16, 16, true)
    vue.setUint16(20, 1, true)
    vue.setUint16(22, 1, true)
    vue.setUint32(24, bufferAudio.sampleRate, true)
    vue.setUint32(28, bufferAudio.sampleRate * 2, true)
    vue.setUint16(32, 2, true)
    vue.setUint16(34, 16, true)
    ecrireTexte(36, 'data')
    vue.setUint32(40, nombreEchantillons * 2, true)

    const canaux = Array.from({ length: bufferAudio.numberOfChannels }, (_, canal) => bufferAudio.getChannelData(canal))
    for (let index = 0; index < nombreEchantillons; index += 1) {
      const mono = canaux.reduce((somme, canal) => somme + canal[index], 0) / canaux.length
      const echantillon = Math.max(-1, Math.min(1, mono))
      vue.setInt16(44 + index * 2, echantillon < 0 ? echantillon * 0x8000 : echantillon * 0x7fff, true)
    }
    return new Blob([wav], { type: 'audio/wav' })
  } finally {
    await contexte.close()
  }
}