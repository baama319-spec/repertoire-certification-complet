<template>
  <header class="admin-header">
    <label><span>⌕</span><input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" :placeholder="placeholder"></label>
    <div class="header-actions">
      <button class="alertes" aria-label="Alertes">♧<b>2</b></button><strong>Alertes (2)</strong><i></i>
      <div ref="menu" class="profil-admin">
        <button type="button" class="declencheur" :aria-expanded="ouvert" @click="ouvert = !ouvert"><Avatar class="user" :photo="utilisateur?.photo_profil" :nom="nomComplet"/><strong class="administrator">{{ nomComplet }}</strong><span>⌄</span></button>
        <nav v-if="ouvert" class="menu" aria-label="Menu du compte"><button type="button" @click="seDeconnecter">⇥ <span>Déconnexion</span></button></nav>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthentification } from '../../services/serviceAuthentification'
import Avatar from '../commun/Avatar.vue'

defineProps({ modelValue: { type: String, default: '' }, placeholder: { type: String, default: 'Recherche globale (Nom, ID Demande, Zone)…' } })
defineEmits(['update:modelValue'])
const router = useRouter()
const { utilisateur, deconnecter } = useAuthentification()
const nomComplet = computed(() => [utilisateur.value?.prenom, utilisateur.value?.nom].filter(Boolean).join(' ') || 'Administrateur')
const ouvert = ref(false)
const menu = ref(null)
const fermer = () => { ouvert.value = false }
const seDeconnecter = async () => { fermer(); await deconnecter(); router.replace('/') }
const clicExterieur = event => { if (menu.value && !menu.value.contains(event.target)) fermer() }
onMounted(() => document.addEventListener('click', clicExterieur))
onBeforeUnmount(() => document.removeEventListener('click', clicExterieur))
</script>

<style scoped>
.admin-header{height:80px;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 28px;border-bottom:1px solid #dce9f8;gap:24px}.admin-header label{height:51px;max-width:680px;flex:1;display:flex;align-items:center;gap:16px;padding:0 16px;border:1px solid #bfdbff;border-radius:13px;background:#f6faff;color:#1265ca;font-size:27px}.admin-header input{border:0;outline:0;background:transparent;width:100%;font:inherit;font-size:14px;color:#12346d}.header-actions{display:flex;align-items:center;gap:15px;color:#174b50;white-space:nowrap}.alertes{position:relative;border:0;background:transparent;color:#075fd0;font-size:29px}.alertes b{position:absolute;right:-3px;top:-5px;width:19px;height:19px;border-radius:50%;background:#fa3b51;color:#fff;font-size:11px;display:grid;place-items:center}.header-actions strong{font-size:14px}.header-actions>i{height:32px;border-left:1px solid #d9e7f7;margin:0 8px}.profil-admin{position:relative}.declencheur{display:flex;align-items:center;gap:10px;border:0;background:transparent;color:inherit;cursor:pointer}.user{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:#10468d;color:#fff;font-size:21px}.administrator{margin-left:2px}.menu{position:absolute;z-index:20;top:calc(100% + 10px);right:0;width:160px;padding:8px;border:1px solid #dceeea;border-radius:8px;background:#fff;box-shadow:0 10px 24px #1d4d861f}.menu button{display:flex;align-items:center;gap:10px;width:100%;min-height:36px;padding:0 10px;border:0;border-radius:5px;background:transparent;color:#dd3951;font:inherit;font-size:11px;text-align:left;cursor:pointer}.menu button:hover{background:#fff0f2}@media(max-width:950px){.administrator,.header-actions>strong:first-of-type,.header-actions>i{display:none}.admin-header{padding:0 16px}.admin-header label{min-width:0}.declencheur{gap:5px}}
</style>
