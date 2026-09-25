const baseUrl = import.meta.env.VITE_API_URL || '/api'

export async function api (path, options = {}) {
  const token = localStorage.getItem('reparsystem-token') || sessionStorage.getItem('reparsystem-token')
  const estFormulaire = options.body instanceof FormData
  let response
  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers: {
        ...(options.body && !estFormulaire ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Token ${token}` } : {}),
        ...options.headers,
      },
    })
  } catch (_) {
    throw new Error('Impossible de joindre le serveur. Vérifiez que l’API est démarrée.')
  }

  const data = await response.json().catch(() => ({}))

  if (response.status === 401) {
    localStorage.removeItem('reparsystem-token')
    sessionStorage.removeItem('reparsystem-token')
    localStorage.removeItem('reparsystem-utilisateur')
    sessionStorage.removeItem('reparsystem-utilisateur')
  }

  if (!response.ok) {
    const erreur = typeof data === 'object' && data !== null
      ? data.detail || Object.values(data).flat().join(' ')
      : ''
    throw new Error(erreur || 'Une erreur est survenue.')
  }
  return data
}
