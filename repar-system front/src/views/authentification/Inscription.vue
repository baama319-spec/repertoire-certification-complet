<template>
  <div class="auth">
    <header>
      <RouterLink to="/" class="brand"><LogoReparSystem :size="48"/><span><b>Repar<span>System</span></b><small>Réparez aujourd'hui, restez connecté demain</small></span></RouterLink>
      <nav><RouterLink to="/"><AppIcon name="home" :size="15"/> Accueil</RouterLink><RouterLink to="/connexion"><AppIcon name="logout" :size="15"/> Se connecter</RouterLink></nav>
    </header>
    <main>
      <section class="visual">
        <div class="copy"><h1><LogoReparSystem :size="56"/> Repar<span>System</span></h1><h2>Votre solution de réparation<br>commence <em>ici</em></h2><p>Créez votre compte gratuitement pour trouver un réparateur qualifié ou proposer vos services.</p><ul><li><AppIcon name="check-circle" :size="17"/> <b>Demandez une réparation<br>en quelques clics</b></li><li><AppIcon name="check-circle" :size="17"/> <b>Accédez à des professionnels<br>vérifiés près de chez vous</b></li><li><AppIcon name="check-circle" :size="17"/> <b>Suivez vos demandes<br>en temps réel</b></li></ul></div>
        <div class="devices"><AppIcon name="smartphone" :size="16"/> Smartphones &amp; Tablettes　<AppIcon name="appliance" :size="16"/> Électroménager　<AppIcon name="television" :size="16"/> TV &amp; Écrans　<AppIcon name="wrench" :size="16"/> Autres appareils</div>
      </section>
      <section class="panel">
        <form @submit.prevent="inscrire">
          <h2>Créer un compte</h2><p>Rejoignez ReparSystem et accédez rapidement à nos services.</p>
          <div class="fields">
            <label>Prénom *<input v-model.trim="prenom" placeholder="Votre prénom" required></label>
            <label>Nom *<input v-model.trim="nom" placeholder="Votre nom" required></label>
            <label><AppIcon name="mail" :size="15"/> Adresse email<input v-model.trim="email" type="email" placeholder="exemple@email.sn" required></label>
            <label><AppIcon name="phone" :size="15"/> Téléphone<input v-model.trim="telephone" type="tel" placeholder="+221 77 000 00 00" required></label>
            <label class="wide"><AppIcon name="shield" :size="15"/> Mot de passe *<span class="pass"><input v-model="motDePasse" :type="showPassword ? 'text' : 'password'" placeholder="Minimum 8 caractères" minlength="8" required><button type="button" :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'" @click="showPassword = !showPassword"><AppIcon :name="showPassword ? 'eye-off' : 'eye'" :size="16"/></button></span></label>
            <label class="wide"><AppIcon name="shield" :size="15"/> Confirmer le mot de passe *<span class="pass"><input v-model="confirmation" :type="showPassword ? 'text' : 'password'" placeholder="Retapez votre mot de passe" minlength="8" required><button type="button" :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'" @click="showPassword = !showPassword"><AppIcon :name="showPassword ? 'eye-off' : 'eye'" :size="16"/></button></span></label>
          </div>
          <label class="terms"><input v-model="accepted" type="checkbox" required> J'accepte les <a>conditions d'utilisation</a> et la <a>politique de confidentialité</a>.</label>
          <p v-if="error" class="error">{{ error }}</p>
          <button class="submit"><AppIcon name="user" :size="16"/> S'inscrire</button>
          <div class="or">Ou s'inscrire avec</div>
          <div class="social"><button type="button"><b>G</b> Google</button><button type="button"><b>f</b> Facebook</button></div>
          <p class="already">Vous avez déjà un compte ? <RouterLink to="/connexion">Se connecter</RouterLink></p>
          <strong v-if="submitted">Compte créé avec succès. Vous pouvez vous connecter.</strong>
        </form>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { routeAccueilUtilisateur, useAuthentification } from '../../services/serviceAuthentification'
import LogoReparSystem from '../../components/commun/LogoReparSystem.vue'
import { checkboxMessage, confirmationMessage, emailMessage, passwordMessage, phoneMessage, requiredMessage } from '../../utils/formValidation'

const router = useRouter()
const { inscrire: creerCompte, utilisateur: utilisateurConnecte } = useAuthentification()
const prenom = ref(''), nom = ref(''), email = ref(''), telephone = ref(''), motDePasse = ref(''), confirmation = ref(''), accepted = ref(false), showPassword = ref(false), error = ref(''), submitted = ref(false)
if (utilisateurConnecte.value) {
  router.replace(routeAccueilUtilisateur(utilisateurConnecte.value))
}
function validerFormulaire () {
  const erreurs = [
    requiredMessage(prenom.value, 'Le prénom'),
    requiredMessage(nom.value, 'Le nom'),
    emailMessage(email.value),
    phoneMessage(telephone.value),
    passwordMessage(motDePasse.value),
    confirmationMessage(motDePasse.value, confirmation.value, 'La confirmation du mot de passe'),
    checkboxMessage(accepted.value, 'les conditions d’utilisation'),
  ].filter(Boolean)

  if (erreurs.length) {
    throw new Error(erreurs[0])
  }
}
async function inscrire () {
  submitted.value = false
  error.value = ''
  try {
    validerFormulaire()
    await creerCompte({ prenom: prenom.value.trim(), nom: nom.value.trim(), email: email.value.trim(), telephone: telephone.value.trim(), password: motDePasse.value })
    submitted.value = true
    router.replace({ path: '/connexion', query: { inscription: 'ok' } })
  } catch (err) { error.value = err.message }
}
</script>

<style scoped>
.auth{min-height:100vh;color:#174b50;background:#f9fcff}.auth header{height:76px;display:flex;align-items:center;justify-content:space-between;padding:0 3%;background:#fff;box-shadow:0 2px 10px #123d7a0d}.brand{display:flex;align-items:center;gap:10px}.brand>i{display:grid;place-items:center;width:53px;height:53px;border-radius:11px;background:#087f70;color:#fff;font-style:normal;font-size:28px}.brand b{display:block;font-size:28px}.brand b span,.copy h1 span,.copy em{color:#087f70}.brand small{display:block;color:#406cc1;font-size:12px}.auth nav{display:flex;gap:20px;align-items:center;font-weight:700;font-size:13px}.auth nav a:last-child{padding:13px 18px;border-radius:8px;background:#087f70;color:#fff}main{display:grid;grid-template-columns:56.4% 43.6%;min-height:calc(100vh - 76px)}.visual{position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;background:linear-gradient(90deg,#061f47cc,#082b5a80),url('../../assets/images/reparateur-hero-reference.png') center/cover;color:#fff}.visual:before,.visual:after{content:'';position:absolute;width:260px;height:260px;border-radius:50%;background:#087f70}.visual:before{left:-135px;top:-135px}.visual:after{right:-135px;bottom:-135px}.copy{position:relative;z-index:1;width:min(510px, calc(100% - 56px));margin:0 auto}.copy h1{font-size:40px;margin:0 0 24px}.copy h1 i{display:inline-grid;place-items:center;width:80px;height:80px;margin-right:17px;border-radius:17px;background:#087f70;font-style:normal}.copy h2{font-size:31px;line-height:1.18;margin:0 0 19px}.copy em{font-style:normal}.copy p{font-size:16px;line-height:1.42}.copy ul{list-style:none;padding:0;margin:30px 0;display:grid;gap:19px}.copy li{font-size:26px}.copy li b{display:inline-block;margin-left:14px;font-size:16px;line-height:1.25;vertical-align:middle}.devices{position:absolute;z-index:1;bottom:45px;left:0;right:0;text-align:center;font-size:12px}.panel{display:grid;place-items:center;padding:12px 8%;background:radial-gradient(circle at 100% 18%,#dceeff 0 105px,transparent 106px),#f9fcff}.panel form{width:min(570px,100%);padding:14px 30px 16px;border:1px solid #e0edf9;border-radius:13px;background:#fff;text-align:center;box-shadow:0 12px 30px #28599012}.user{display:grid;place-items:center;width:43px;height:43px;margin:auto;border-radius:50%;background:#087f70;color:#fff;font-style:normal;font-size:24px}.panel h2{font-size:25px;margin:4px 0}.panel form>p{margin:0 0 12px;color:#547bc4;font-size:11px}.fields{display:grid;grid-template-columns:1fr 1fr;gap:11px 13px}.fields label{display:block;text-align:left;font-size:10px;font-weight:700}.fields .wide{grid-column:1/-1}.fields label small{font-weight:400}.fields input,.fields select{box-sizing:border-box;display:block;width:100%;height:36px;margin-top:5px;padding:0 11px;border:1px solid #b6d5ff;border-radius:7px;background:#fff;font:inherit;font-size:10px;outline-color:#087f70}.pass{position:relative;display:block}.pass button{position:absolute;right:8px;bottom:5px;background:transparent;color:#7998d4;font-size:14px}.terms{display:block;margin:12px 0;text-align:left;color:#547bc4;font-size:10px}.terms input{margin:0 6px 0 0;accent-color:#087f70}.terms a,.already a{color:#087f70;font-weight:700}.submit{display:block;width:100%;height:39px;border-radius:8px;background:#087f70;color:#fff;font-size:11px}.or{display:flex;align-items:center;gap:15px;margin:12px 0 9px;color:#406ec0;font-size:10px;font-weight:700}.or:before,.or:after{content:'';flex:1;border-top:1px solid #cfe0f5}.social{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}.social button{height:34px;border:1px solid #b6d5ff;border-radius:7px;background:#fff;color:#315b9f;font-size:10px}.social b{font-size:15px;margin-right:7px}.social button:first-child b{color:#ea4335}.social button:last-child b{color:#1877f2}.panel .already{margin:0;color:#174b50;font-size:10px}.error{color:#e23b57!important;font-weight:700}.panel strong{display:block;margin-top:8px;color:#00a76c;font-size:10px}@media(max-width:900px){main{grid-template-columns:1fr}.visual{min-height:500px}.panel{padding:35px 20px}.devices{display:none}.copy{width:80%}}@media(max-width:500px){.auth header{padding:0 15px}.brand b{font-size:20px}.brand small,.auth nav a:first-child{display:none}.brand>i{width:45px;height:45px}.visual{min-height:460px}.copy{margin-top:30px}.copy h1{font-size:28px}.copy h1 i{width:55px;height:55px;margin-right:8px}.copy h2{font-size:25px}.copy p{font-size:13px}.panel{padding:22px 18px}.panel form{padding:22px 18px}.panel h2{font-size:27px}.fields{grid-template-columns:1fr;gap:13px}.fields .wide{grid-column:auto}.fields input,.fields select{height:45px;font-size:inherit;margin-top:7px}.terms{font-size:11px;margin:16px 0}.submit{height:51px;font-size:13px}.or{margin:20px 0 12px;font-size:11px}.social{grid-template-columns:1fr}.social button{height:42px;font-size:11px}.panel .already{font-size:12px}}
</style>
<style scoped>
@media (min-width: 501px) {
  .fields { grid-template-columns: 1fr; gap: 16px 13px; }
  .fields .wide { grid-column: auto; }
  .fields input, .fields select { margin-top: 7px; }
  .terms { margin: 16px 0; }
  .or { margin: 16px 0 12px; }
  .social { margin-bottom: 14px; }
}
</style>
