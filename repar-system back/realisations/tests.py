from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from reparateurs.models import Reparateur
from specialites.models import Specialite
from .models import Realisation


class RealisationAccessTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.reparateur_user = user_model.objects.create_user(
			email="artisan-un@example.com", password="password123", nom="Un", prenom="Artisan",
			role=user_model.Role.REPARATEUR,
		)
		self.autre_user = user_model.objects.create_user(
			email="artisan-deux@example.com", password="password123", nom="Deux", prenom="Artisan",
			role=user_model.Role.REPARATEUR,
		)
		self.reparateur = Reparateur.objects.create(utilisateur=self.reparateur_user)
		self.reparateur.statut_verification = Reparateur.StatutVerification.VALIDEE
		self.reparateur.save(update_fields=("statut_verification",))
		self.autre_reparateur = Reparateur.objects.create(
			utilisateur=self.autre_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)
		self.ma_realisation = Realisation.objects.create(reparateur=self.reparateur, titre="Ma réparation", description="Travail personnel")
		self.realisation_autre = Realisation.objects.create(reparateur=self.autre_reparateur, titre="Autre réparation", description="Travail d’un autre")

	def test_reparateur_ne_voit_que_ses_realisations_meme_avec_un_filtre_autre_id(self):
		self.client.force_authenticate(self.reparateur_user)

		response = self.client.get(f"/api/realisations/?reparateur={self.autre_reparateur.pk}")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data["results"]], [self.ma_realisation.pk])

	def test_reparateur_ne_peut_pas_consulter_la_realisation_d_un_autre(self):
		self.client.force_authenticate(self.reparateur_user)

		response = self.client.get(f"/api/realisations/{self.realisation_autre.pk}/")

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_reparateur_peut_modifier_sa_propre_realisation(self):
		self.client.force_authenticate(self.reparateur_user)

		response = self.client.patch(
			f"/api/realisations/{self.ma_realisation.pk}/",
			{"titre": "Titre modifié"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.ma_realisation.refresh_from_db()
		self.assertEqual(self.ma_realisation.titre, "Titre modifié")

	def test_reparateur_ne_peut_pas_modifier_la_realisation_d_un_autre(self):
		self.client.force_authenticate(self.reparateur_user)

		response = self.client.patch(
			f"/api/realisations/{self.realisation_autre.pk}/",
			{"titre": "Modification interdite"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_espace_mes_realisations_ne_retourne_que_les_realisations_du_compte(self):
		self.client.force_authenticate(self.reparateur_user)

		response = self.client.get("/api/realisations/mes/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data["results"]], [self.ma_realisation.pk])

	def test_espace_mes_realisations_filtre_aussi_un_compte_client_avec_profil_reparateur(self):
		user_model = get_user_model()
		client_pro_user = user_model.objects.create_user(
			email="artisan-client@example.com", password="password123", nom="Client", prenom="Artisan",
			role=user_model.Role.CLIENT,
		)
		client_profil = Reparateur.objects.create(
			utilisateur=client_pro_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)
		realisation_client_pro = Realisation.objects.create(
			reparateur=client_profil, titre="Réalisation du profil", description="Portfolio du compte client",
		)
		self.client.force_authenticate(client_pro_user)

		response = self.client.get("/api/realisations/mes/")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data["results"]], [realisation_client_pro.pk])

	def test_candidat_en_attente_ne_peut_pas_voir_ou_publier_ses_realisations(self):
		candidat_user = get_user_model().objects.create_user(
			email="candidat-pending@example.com", password="password123", nom="Candidat", prenom="Test",
		)
		candidat = Reparateur.objects.create(utilisateur=candidat_user)
		realisation = Realisation.objects.create(
			reparateur=candidat, titre="Portfolio en attente", description="Ne doit pas être public.",
		)
		self.client.force_authenticate(candidat_user)
		specialite, _ = Specialite.objects.get_or_create(nom="Réparation en attente")

		mes_realisations = self.client.get("/api/realisations/mes/")
		fiche_publique = self.client.get(f"/api/realisations/{realisation.pk}/")
		creation = self.client.post(
			"/api/realisations/",
			{
				"titre": "Nouvelle réalisation",
				"description": "Intervention non autorisée.",
				"specialite": specialite.pk,
			},
			format="json",
		)

		self.assertEqual(mes_realisations.status_code, 403)
		self.assertEqual(fiche_publique.status_code, 404)
		self.assertEqual(creation.status_code, 403)
