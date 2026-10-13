<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
defineProps({ realisation: { type: Object, required: true } })
defineEmits(['editer', 'supprimer'])
const imageAgrandie = ref(null)
const fermerAvecEchap = event => { if (event.key === 'Escape') imageAgrandie.value = null }
onMounted(() => window.addEventListener('keydown', fermerAvecEchap))
onBeforeUnmount(() => window.removeEventListener('keydown', fermerAvecEchap))
const date = valeur => new Intl.DateTimeFormat('fr-FR', { dateStyle: 'medium' }).format(new Date(valeur))
</script>
<template><article class="carte-realisation"><div class="comparaison"><figure><button v-if="realisation.photo_avant_url" class="photo-zoom" type="button" aria-label="Agrandir la photo avant réparation" @click="imageAgrandie={src:realisation.photo_avant_url,alt:'Avant réparation'}"><img :src="realisation.photo_avant_url" alt="Avant réparation"></button><span v-else class="sans-photo">Avant</span><figcaption>Avant</figcaption></figure><AppIcon name="arrow-right" :size="18"/><figure><button v-if="realisation.photo_apres_url" class="photo-zoom" type="button" aria-label="Agrandir la photo après réparation" @click="imageAgrandie={src:realisation.photo_apres_url,alt:'Après réparation'}"><img :src="realisation.photo_apres_url" alt="Après réparation"></button><span v-else class="sans-photo">Après</span><figcaption class="apres">Après</figcaption></figure></div><h2>{{ realisation.titre }}</h2><p>{{ realisation.description }}</p><div class="infos"><span>{{ realisation.specialite_nom }}</span><time>{{ date(realisation.date_realisation) }}</time></div><footer><button class="editer" @click="$emit('editer', realisation)">Éditer</button><button class="supprimer" @click="$emit('supprimer', realisation)">Supprimer</button></footer><Teleport to="body"><div v-if="imageAgrandie" class="visionneuse" role="dialog" aria-modal="true" :aria-label="imageAgrandie.alt" @click.self="imageAgrandie=null"><button class="fermer-visionneuse" type="button" aria-label="Fermer l’image" @click="imageAgrandie=null"><AppIcon name="close" :size="24"/></button><img :src="imageAgrandie.src" :alt="imageAgrandie.alt"></div></Teleport></article></template>
<style scoped>.carte-realisation{padding:11px;border:1px solid #e1eaf6;border-radius:8px;background:#fff;color:#0a2d68;box-shadow:0 2px 7px #1647820a}.comparaison{display:grid;grid-template-columns:1fr 0 1fr;align-items:center}.comparaison figure{height:112px;position:relative;margin:0;overflow:hidden;border-radius:5px;background:#e7f5f1}.photo-zoom{display:block;width:100%;height:100%;padding:0;border:0;background:transparent;cursor:zoom-in}.comparaison img{width:100%;height:100%;object-fit:cover}.sans-photo{display:grid;place-items:center;height:100%;color:#8093ae;font-size:10px}.comparaison>b{z-index:1;width:24px;height:24px;margin-left:-12px;display:grid;place-items:center;border-radius:50%;background:#fff;color:#087f70;font-size:14px}.comparaison figcaption{position:absolute;bottom:6px;left:6px;padding:3px 6px;border-radius:4px;background:#14243e;color:#fff;font-size:8px;pointer-events:none}.comparaison .apres{background:#087f70}.carte-realisation h2{overflow:hidden;margin:11px 0 4px;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.carte-realisation p{overflow:hidden;min-height:15px;margin:0 0 8px;color:#6981a6;font-size:9px;text-overflow:ellipsis;white-space:nowrap}.infos{display:flex;justify-content:space-between;gap:4px;color:#6882ab;font-size:8px}.infos span{overflow:hidden;max-width:55%;padding:5px 7px;border-radius:13px;background:#e7f5f1;color:#087f70;font-weight:700;text-overflow:ellipsis;white-space:nowrap}.infos time{padding-top:5px;white-space:nowrap}footer{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}footer button{height:27px;border-radius:5px;background:#fff;font-size:9px;font-weight:700}.editer{border:1px solid #087f70;color:#087f70}.supprimer{border:1px solid #ff8b94;color:#f04a5a}.visionneuse{position:fixed;z-index:1000;inset:0;display:grid;place-items:center;padding:55px 24px 24px;background:#061226ed;cursor:zoom-out}.visionneuse img{max-width:min(1200px,100%);max-height:100%;object-fit:contain;border-radius:8px}.fermer-visionneuse{position:absolute;top:16px;right:20px;width:42px;height:42px;border:1px solid #ffffff55;border-radius:50%;background:#ffffff18;color:white;font-size:30px;line-height:1;cursor:pointer}

/* Mise en page plus lisible du portfolio réparateur. */
.carte-realisation{display:flex;min-width:0;flex-direction:column;padding:16px;border-color:#dce7f5;border-radius:13px;box-shadow:0 5px 18px rgba(22,58,105,.08);transition:transform .18s ease,box-shadow .18s ease}
.carte-realisation:hover{transform:translateY(-2px);box-shadow:0 10px 26px rgba(22,58,105,.13)}
.comparaison{grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr)}
.comparaison figure{height:156px;border-radius:9px}
.comparaison>b{width:30px;height:30px;margin:0 auto;border:1px solid #e4ecf7;box-shadow:0 2px 8px #102a521a}
.comparaison figcaption{bottom:9px;left:9px;padding:5px 9px;border-radius:5px;font-size:11px;font-weight:700}
.carte-realisation h2{margin:14px 0 6px;color:#0a2d68;font-size:17px;line-height:1.35}
.carte-realisation p{display:-webkit-box;min-height:38px;margin:0 0 13px;color:#647895;font-size:13px;line-height:1.5;text-overflow:clip;white-space:normal;-webkit-box-orient:vertical;-webkit-line-clamp:2}
.infos{align-items:center;gap:10px;margin-top:auto;color:#607895;font-size:11px}
.infos span{max-width:65%;padding:7px 10px;font-size:11px}
.infos time{padding-top:0;font-size:11px}
.carte-realisation>footer{gap:10px;margin-top:14px}
.carte-realisation>footer button{height:38px;border-radius:7px;font-size:12px;transition:background .15s ease,color .15s ease}
.carte-realisation>footer .editer:hover{background:#087f70;color:#fff}
.carte-realisation>footer .supprimer:hover{background:#f04a5a;color:#fff}
@media(max-width:800px){.comparaison figure{height:145px}.carte-realisation{padding:13px}.comparaison{grid-template-columns:minmax(0,1fr) 30px minmax(0,1fr)}.comparaison figure{height:145px}.carte-realisation h2{font-size:16px}.carte-realisation p{font-size:12px}}
</style>
