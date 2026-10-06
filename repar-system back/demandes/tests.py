from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from clients.models import Client
from localisations.models import Localisation
from notifications.models import Notification
from reparateurs.models import Reparateur
from .models import DemandeMiseEnRelation


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
				"appareil": "Smartphone · Samsung Galaxy S21",
				"description_probleme": "Mon téléphone ne charge plus depuis hier.",
				"localisation": self.localisation.pk,
				"mode_intervention": "DOMICILE",
				"adresse_intervention": "Dakar Plateau, rue 10",
				"source": "RECOMMANDATION_IA",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["client"], self.client_profil.pk)
		self.assertEqual(response.data["appareil"], "Smartphone · Samsung Galaxy S21")
		self.assertEqual(response.data["statut"], DemandeMiseEnRelation.Statut.EN_ATTENTE)
		self.assertEqual(response.data["mode_intervention"], "DOMICILE")
		self.assertEqual(response.data["adresse_intervention"], "Dakar Plateau, rue 10")

	def test_description_trop_courte_est_refusee(self):
		response = self.client.post(
			"/api/demandes/",
			{
				"description_probleme": "Panne",
				"localisation": self.localisation.pk,
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(DemandeMiseEnRelation.objects.exists())

	def test_un_compte_client_avec_profil_reparateur_peut_lister_ses_demandes_entrantes(self):
		user_model = get_user_model()
		repairer_user = user_model.objects.create_user(
			email="double-role@example.com",
			password="password123",
			nom="Ly",
			prenom="Aziz",
			role=user_model.Role.CLIENT,
		)
		repairer_profile = Reparateur.objects.create(
			utilisateur=repairer_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)
		client_user = user_model.objects.create_user(
			email="autre-client@example.com",
			password="password123",
			nom="Client",
			prenom="Aly",
		)
		client_profile = Client.objects.create(utilisateur=client_user)
		demande = DemandeMiseEnRelation.objects.create(
			client=client_profile,
			reparateur=repairer_profile,
			localisation=Localisation.objects.create(
				nom="Dakar Plateau",
				adresse="Dakar Plateau",
				quartier="Dakar Plateau",
				ville="Dakar",
			),
			description_probleme="Écran du téléphone cassé après une chute.",
		)

		self.client.force_authenticate(repairer_user)
		response = self.client.get("/api/demandes/?contexte=reparateur")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([item["id"] for item in response.data["results"]], [demande.pk])

	def test_candidat_en_attente_ne_peut_pas_voir_les_demandes_entrantes(self):
		user_model = get_user_model()
		candidat = user_model.objects.create_user(
			email="candidat-pending@example.com", password="password123", nom="Candidat", prenom="Test",
		)
		profil = Reparateur.objects.create(utilisateur=candidat)
		DemandeMiseEnRelation.objects.create(
			client=self.client_profil,
			reparateur=profil,
			localisation=self.localisation,
			description_probleme="Demande assignée avant validation.",
		)

		self.client.force_authenticate(candidat)
		response = self.client.get("/api/demandes/?contexte=reparateur")

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	@patch("demandes.views.envoyer_notification_n8n")
	def test_creation_demande_ciblee_notifie_le_reparateur(self, notifier_n8n):
		user_model = get_user_model()
		repairer_user = user_model.objects.create_user(
			email="reparateur@example.com",
			password="password123",
			nom="Test",
			prenom="Reparateur",
			role=user_model.Role.REPARATEUR,
		)
		repairer_profile = Reparateur.objects.create(
			utilisateur=repairer_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)

		response = self.client.post(
			"/api/demandes/",
			{
				"description_probleme": "Mon téléphone ne charge plus depuis hier.",
				"localisation": self.localisation.pk,
				"reparateur": repairer_profile.pk,
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(
			Notification.objects.filter(
				utilisateur=repairer_user,
				type=Notification.Type.NOUVELLE_DEMANDE,
			).exists()
		)
		notifier_n8n.assert_called_once_with(
			repairer_user,
			"Nouvelle demande de réparation",
			"Un client vous a envoyé une nouvelle demande de réparation.",
			"nouvelle_demande",
		)

	def test_demande_ne_peut_pas_etre_ciblee_vers_un_candidat_non_valide(self):
		candidat = get_user_model().objects.create_user(
			email="candidat-non-valide@example.com", password="password123", nom="Candidat", prenom="Test",
		)
		profil = Reparateur.objects.create(utilisateur=candidat)

		response = self.client.post(
			"/api/demandes/",
			{
				"description_probleme": "Mon téléphone ne charge plus depuis hier.",
				"localisation": self.localisation.pk,
				"reparateur": profil.pk,
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AcceptationDemandeTests(APITestCase):
	@patch("demandes.views.envoyer_notification_n8n")
	def test_reparateur_accepte_demande_et_declenche_notification(self, notifier_n8n):
		user_model = get_user_model()
		client_user = user_model.objects.create_user(
			email="babaamadouba1@gmail.com",
			password="password123",
			nom="Test",
			prenom="Client",
			role=user_model.Role.CLIENT,
		)
		repairer_user = user_model.objects.create_user(
			email="reparateur@example.com",
			password="password123",
			nom="Test",
			prenom="Reparateur",
			role=user_model.Role.REPARATEUR,
		)
		client_profile = Client.objects.create(utilisateur=client_user)
		repairer_profile = Reparateur.objects.create(
			utilisateur=repairer_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)
		localisation = Localisation.objects.create(
			nom="Dakar Plateau",
			adresse="Dakar Plateau",
			quartier="Dakar Plateau",
			ville="Dakar",
		)
		demande = DemandeMiseEnRelation.objects.create(
			client=client_profile,
			reparateur=repairer_profile,
			localisation=localisation,
			description_probleme="Simulation de test : réparation téléphone.",
		)

		self.client.force_authenticate(repairer_user)
		response = self.client.post(
			f"/api/demandes/{demande.pk}/accepter/",
			{},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		demande.refresh_from_db()
		self.assertEqual(demande.statut, DemandeMiseEnRelation.Statut.ACCEPTEE)
		self.assertTrue(
			Notification.objects.filter(
				utilisateur=client_user,
				type=Notification.Type.DEMANDE_ACCEPTEE,
			).exists()
		)
		notifier_n8n.assert_called_once_with(
			client_user,
			"Demande acceptée",
			"Votre demande a été acceptée.",
			"demande_acceptee",
		)

	@patch("demandes.views.envoyer_notification_n8n")
	def test_compte_client_avec_profil_reparateur_assigne_peut_accepter(self, notifier_n8n):
		user_model = get_user_model()
		repairer_user = user_model.objects.create_user(
			email="aziz@example.com",
			password="password123",
			nom="Ly",
			prenom="Aziz",
		)
		client_user = user_model.objects.create_user(
			email="aly@example.com",
			password="password123",
			nom="Client",
			prenom="Aly",
		)
		repairer_profile = Reparateur.objects.create(
			utilisateur=repairer_user,
			statut_verification=Reparateur.StatutVerification.VALIDEE,
		)
		client_profile = Client.objects.create(utilisateur=client_user)
		demande = DemandeMiseEnRelation.objects.create(
			client=client_profile,
			reparateur=repairer_profile,
			localisation=Localisation.objects.create(
				nom="Dakar Plateau",
				adresse="Dakar Plateau",
				quartier="Dakar Plateau",
				ville="Dakar",
			),
			description_probleme="Réparer le téléphone qui ne s’allume plus.",
		)

		self.client.force_authenticate(repairer_user)
		response = self.client.post(f"/api/demandes/{demande.pk}/accepter/", {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		demande.refresh_from_db()
		self.assertEqual(demande.statut, DemandeMiseEnRelation.Statut.ACCEPTEE)
		notifier_n8n.assert_called_once()


class AnnulationDemandeClientTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.client_user = user_model.objects.create_user(
			email="proprietaire@example.com", password="password123", nom="Client", prenom="Propriétaire",
			role=user_model.Role.CLIENT,
		)
		self.autre_client = user_model.objects.create_user(
			email="autre@example.com", password="password123", nom="Autre", prenom="Client",
			role=user_model.Role.CLIENT,
		)
		self.profil_client = Client.objects.create(utilisateur=self.client_user)
		self.localisation = Localisation.objects.create(
			nom="Dakar Plateau", adresse="Dakar Plateau", quartier="Dakar Plateau", ville="Dakar",
		)
		self.demande = DemandeMiseEnRelation.objects.create(
			client=self.profil_client,
			localisation=self.localisation,
			description_probleme="Le téléphone ne charge plus depuis hier.",
		)

	def test_client_peut_annuler_sa_demande_en_attente(self):
		self.client.force_authenticate(self.client_user)

		response = self.client.post(f"/api/demandes/{self.demande.pk}/annuler/", {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.demande.refresh_from_db()
		self.assertEqual(self.demande.statut, DemandeMiseEnRelation.Statut.ANNULEE)
		self.assertIsNotNone(self.demande.date_reponse)

	def test_autre_client_ne_peut_pas_annuler_la_demande(self):
		self.client.force_authenticate(self.autre_client)

		response = self.client.post(f"/api/demandes/{self.demande.pk}/annuler/", {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.demande.refresh_from_db()
		self.assertEqual(self.demande.statut, DemandeMiseEnRelation.Statut.EN_ATTENTE)

	def test_client_ne_peut_pas_annuler_une_demande_deja_acceptee(self):
		self.demande.statut = DemandeMiseEnRelation.Statut.ACCEPTEE
		self.demande.save(update_fields=["statut"])
		self.client.force_authenticate(self.client_user)

		response = self.client.post(f"/api/demandes/{self.demande.pk}/annuler/", {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.demande.refresh_from_db()
		self.assertEqual(self.demande.statut, DemandeMiseEnRelation.Statut.ACCEPTEE)



class RefusationDemandeTests(APITestCase):
	@patch("demandes.views.envoyer_notification_n8n")
	def test_reparateur_refuse_demande_et_mise_a_jour_du_statut(self, notifier_n8n):
		user_model = get_user_model()
		repairer_user = user_model.objects.create_user(
			email="refus-reparateur@example.com",
			password="password123",
			nom="Réparateur",
			prenom="Test",
			role=user_model.Role.REPARATEUR,
		)
		client_user = user_model.objects.create_user(
			email="refus-client@example.com",
			password="password123",
			nom="Client",
			prenom="Test",
			role=user_model.Role.CLIENT,
		)
		demande = DemandeMiseEnRelation.objects.create(
			client=Client.objects.create(utilisateur=client_user),
			reparateur=Reparateur.objects.create(
				utilisateur=repairer_user,
				statut_verification=Reparateur.StatutVerification.VALIDEE,
			),
			localisation=Localisation.objects.create(
				nom="Dakar Plateau",
				adresse="Dakar Plateau",
				quartier="Dakar Plateau",
				ville="Dakar",
			),
			description_probleme="Réparer le téléphone qui ne s’allume plus.",
		)

		self.client.force_authenticate(repairer_user)
		response = self.client.post(f"/api/demandes/{demande.pk}/refuser/", {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		demande.refresh_from_db()
		self.assertEqual(demande.statut, DemandeMiseEnRelation.Statut.REFUSEE)
		notifier_n8n.assert_called_once()
