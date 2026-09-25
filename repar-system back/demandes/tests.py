from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from localisations.models import Localisation


class CreationDemandeTests(APITestCase):
	def setUp(self):
		self.utilisateur = get_user_model().objects.create_user(
			email="client@example.com",
			password="password123",
			nom="Fall",
			prenom="Mamadou",
		)
		self.client_profil = Client.objects.create(utilisateur=self.utilisateur)
		self.localisation = Localisation.objects.create(
			nom="Dakar Plateau",
			adresse="Dakar Plateau",
			quartier="Dakar Plateau",
			ville="Dakar",
		)
		self.client.force_authenticate(self.utilisateur)

	def test_client_connecte_peut_creer_demande_sans_envoyer_client(self):
		response = self.client.post(
			"/api/demandes/",
			{
				"description_probleme": "Mon téléphone ne charge plus depuis hier.",
				"localisation": self.localisation.pk,
				"source": "RECOMMANDATION_IA",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["client"], self.client_profil.pk)
