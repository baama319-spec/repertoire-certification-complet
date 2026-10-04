export function requiredMessage(value, label) {
  if (value === null || value === undefined || String(value).trim() === '') {
    return `${label} est obligatoire.`
  }
  return ''
}

export function minLengthMessage(value, label, min) {
  if (value === null || value === undefined || String(value).trim().length < min) {
    return `${label} doit contenir au moins ${min} caractères.`
  }
  return ''
}

export function emailMessage(value) {
  if (!value || String(value).trim() === '') return 'L’adresse e-mail est obligatoire.'
  const email = String(value).trim()
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!regex.test(email)) return 'Veuillez saisir une adresse e-mail valide.'
  return ''
}

export function phoneMessage(value) {
  if (!value || String(value).trim() === '') return 'Le numéro de téléphone est obligatoire.'
  const phone = String(value).trim()
  const regex = /^\+?[0-9\s().-]{8,20}$/
  if (!regex.test(phone)) return 'Le numéro de téléphone n’est pas valide.'
  return ''
}

export function passwordMessage(value) {
  if (!value || String(value).trim() === '') return 'Le mot de passe est obligatoire.'
  if (String(value).length < 8) return 'Le mot de passe doit contenir au moins 8 caractères.'
  if (!/[A-Z]/.test(value) || !/[a-z]/.test(value) || !/[0-9]/.test(value)) {
    return 'Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre.'
  }
  return ''
}

export function confirmationMessage(value, confirmation, label = 'La confirmation') {
  if (!value || String(value).trim() === '') return `${label} est obligatoire.`
  if (String(value) !== String(confirmation)) return 'Les deux valeurs ne correspondent pas.'
  return ''
}

export function arrayMessage(value, label, minimum = 1) {
  if (!Array.isArray(value) || value.length < minimum) {
    return `Veuillez sélectionner au moins ${minimum} ${label}.`
  }
  return ''
}

export function numberRangeMessage(value, label, min, max) {
  const number = Number(value)
  if (!Number.isFinite(number) || number < min || number > max) {
    return `${label} doit être compris entre ${min} et ${max}.`
  }
  return ''
}

export function checkboxMessage(value, label) {
  if (!value) return `Veuillez accepter ${label}.`
  return ''
}
