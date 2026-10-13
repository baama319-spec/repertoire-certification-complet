<script setup>
import LogoReparSystem from '../commun/LogoReparSystem.vue'
</script>

<template>
	<footer class="footer">
		<div class="footer-grid">
			<section>
				<div class="brand footer-brand"><LogoReparSystem :size="42"/><span>ReparSystem</span></div>
				<p>La solution n°1 au Sénégal pour trouver des réparateurs qualifiés et vérifiés au Sénégal. Trouvez l'expert de l'électronique en quelques clics.</p>
			</section>
			<section><h4>Services</h4><a>Électricité</a><a>Plomberie</a><a>Électroménager</a><a>Climatisation</a><a>Informatique</a></section>
			<section><h4>Société</h4><a>À propos</a><a>Comment ça marche</a><a>Devenir partenaire</a><a>Blog</a><a>Contact</a></section>
			<section class="footer-contact-section">
				<h4>Contact</h4>
				<a class="footer-contact" href="https://maps.google.com/?q=Dakar,+Sénégal">
					<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>
					Dakar, Sénégal
				</a>
				<a class="footer-contact" href="tel:+221330000000">
					<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2A19.8 19.8 0 0 1 11.2 19a19.4 19.4 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8 8.9a16 16 0 0 0 6 6l1.2-1.3a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.8 2.1Z"/></svg>
					+221 33 000 00 00
				</a>
				<a class="footer-contact" href="mailto:contact@reparsystem.com">
					<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>
					contact@reparsystem.com
				</a>
			</section>
		</div>
		<div class="copyright"><span>© 2024 REPARSYSTEM. TOUS DROITS RÉSERVÉS.</span><span>MENTIONS LÉGALES　 CONFIDENTIALITÉ　 FAQ</span></div>
	</footer>
</template>

<style scoped>
.footer {
  background: #081329;
  color: #7e899c;
  padding: 62px max(5.5%, 48px) 26px;
  font-size: 11px;
}
.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1.2fr;
  gap: 34px;
}
.footer-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #fff;
  font-size: 20px;
  font-weight: 800;
}
.footer h4 {
  margin: 0 0 14px;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}
.footer a {
  display: block;
  color: #c5ced8;
  margin-bottom: 8px;
  font-size: 11px;
}
.footer a:hover {
  color: #fff;
}
.footer-contact {
  display: flex;
  align-items: center;
  gap: 8px;
}
.footer-contact svg {
  width: 14px;
  height: 14px;
  flex: none;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.copyright {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 30px;
  padding-top: 18px;
  border-top: 1px solid rgba(255,255,255,0.12);
  color: #cfe3e0;
  font-size: 10px;
  text-transform: uppercase;
}
@media(max-width:800px){
  .footer-grid{grid-template-columns:1fr 1fr;gap:35px}
  .copyright{flex-direction:column;gap:14px}
}
</style>
