<template>
  <div class="auth"><header><RouterLink to="/" class="brand"><LogoReparSystem :size="42"/> Repar<span>System</span></RouterLink><nav><RouterLink to="/">Accueil</RouterLink><RouterLink to="/inscription">S'inscrire</RouterLink></nav></header><main><section class="visual"><div class="copy"><h1><LogoReparSystem :size="58"/> Repar<span>System</span></h1><h2>Des solutions de réparation à <em>portée de main</em></h2><p>Trouvez rapidement un réparateur qualifié ou gérez vos demandes en toute simplicité.</p></div></section><section class="panel"><form @submit.prevent="soumettre"><h2>Connexion</h2><p>Accédez à votre espace Client ou Réparateur.</p><label>Adresse e-mail<input v-model.trim="email" type="email" required></label><label>Mot de passe<span class="pass"><input v-model="password" :type="show ? 'text' : 'password'" required><button type="button" @click="show = !show">⊘</button></span></label><label class="remember"><input v-model="remember" type="checkbox"> Se souvenir de moi</label><p v-if="error" class="error">{{ error }}</p><button class="submit" :disabled="loading">{{ loading ? 'Connexion…' : 'SE CONNECTER' }}</button><RouterLink to="/inscription" class="create">Créer un compte gratuitement</RouterLink></form></section></main></div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthentification } from '../../services/serviceAuthentification'
import LogoReparSystem from '../../components/commun/LogoReparSystem.vue'

const router = useRouter()
const { connecter } = useAuthentification()
const email = ref(''), password = ref(''), show = ref(false), remember = ref(true), loading = ref(false), error = ref('')
async function soumettre () {
  error.value = ''; loading.value = true
  try {
    const utilisateur = await connecter({ email: email.value, password: password.value, remember: remember.value })
    const destination = router.currentRoute.value.query.redirection
    // Un compte Client + Réparateur démarre côté Client ; il change ensuite
    // volontairement d'espace depuis le menu du compte.
    const compteClientEtReparateur = utilisateur.role === 'CLIENT' && utilisateur.profil_reparateur
    router.push(typeof destination === 'string' ? destination : utilisateur.role === 'ADMINISTRATEUR' ? '/admin' : compteClientEtReparateur ? '/client/demandes' : utilisateur.role === 'REPARATEUR' ? '/pro/demandes' : '/client/demandes')
  } catch (err) { error.value = err.message } finally { loading.value = false }
}
</script>

<style scoped>
.auth{min-height:100vh;color:#174b50;background:#f9fcff}.auth header{height:76px;display:flex;align-items:center;justify-content:space-between;padding:0 5%;background:#fff}.brand{display:flex;align-items:center;gap:8px;font-size:26px;font-weight:800}.brand span,.copy span,.copy em{color:#087f70}.auth nav{display:flex;gap:22px}.auth nav a:last-child,.submit{background:#087f70;color:#fff;border-radius:8px;padding:12px 18px}main{display:grid;grid-template-columns:1fr 1fr;min-height:calc(100vh - 76px)}.visual{display:grid;place-items:center;background:linear-gradient(90deg,#061f47cc,#082b5a80),url('../../assets/images/reparateur-hero-reference.png') center/cover;color:#fff}.copy{max-width:480px;margin:0 auto;padding:25px;text-align:center;transform:translateY(-50px)}.copy h1{display:flex;align-items:center;justify-content:center;gap:14px;font-size:42px}.copy h1 :deep(.logo-reparsystem){background:#fff;border-radius:12px;padding:4px}.copy h2{font-size:32px}.copy em{font-style:normal}.panel{display:grid;place-items:center;padding:30px}.panel form{width:min(440px,100%);padding:36px;border-radius:13px;background:#fff;box-shadow:0 12px 30px #28599012;text-align:center}.panel label{display:block;margin-top:20px;text-align:left;font-weight:700}.panel input{box-sizing:border-box;width:100%;height:48px;margin-top:8px;border:1px solid #b6d5ff;border-radius:8px;padding:0 12px}.pass{position:relative;display:block}.pass button{position:absolute;right:10px;bottom:12px;background:transparent}.remember input{width:auto;height:auto}.submit,.create{box-sizing:border-box;display:block;width:100%;border:0;font-weight:700}.submit{margin-top:20px}.create{margin-top:14px;color:#087f70}.error{color:#d22;font-weight:700}@media(max-width:800px){main{grid-template-columns:1fr}.visual{display:none}}
</style>
