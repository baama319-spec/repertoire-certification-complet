import { api } from './api'

const liste = reponse => Array.isArray(reponse) ? reponse : reponse.results || []

export const chargerAvis = async () => {
	const avis = []
	let page = 1
	let pagesSuivantes = true

	while (pagesSuivantes) {
		const reponse = await api(`/avis/?page=${page}`)
		if (Array.isArray(reponse)) return reponse
		avis.push(...liste(reponse))
		pagesSuivantes = Boolean(reponse.next)
		page += 1
	}

	return avis
}

export const creerAvis = donnees => api('/avis/', {
	method: 'POST',
	body: JSON.stringify(donnees),
})
