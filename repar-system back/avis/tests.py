from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from clients.models import Client
from demandes.models import DemandeMiseEnRelation
from localisations.models import Localisation
from reparateurs.models import Reparateur


class AvisTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.client_user = self.user_model.objects.create_user(
            email="client-avis@example.com",
            password="password123",
            nom="Client",
            prenom="Avis",
            role=self.user_model.Role.CLIENT,
        )
        self.reparateur_user = self.user_model.objects.create_user(
            email="reparateur-avis@example.com",
            password="password123",
            nom="Reparateur",
            prenom="Avis",
            role=self.user_model.Role.REPARATEUR,
        )
        self.client_profile = Client.objects.create(utilisateur=self.client_user)
        self.reparateur = Reparateur.objects.create(
            utilisateur=self.reparateur_user,
            statut_verification=Reparateur.StatutVerification.VALIDEE,
        )
        self.localisation = Localisation.objects.create(
            nom="Dakar Plateau",
            adresse="Dakar Plateau",
            quartier="Dakar Plateau",
            ville="Dakar",
        )
        self.demande = DemandeMiseEnRelation.objects.create(
            client=self.client_profile,
            reparateur=self.reparateur,
            localisation=self.localisation,
            description_probleme="Le téléphone ne charge plus.",
            statut=DemandeMiseEnRelation.Statut.ACCEPTEE,
        )

    def test_client_peut_creer_un_seul_avis_pour_une_demande_acceptee(self):
        self.client.force_authenticate(self.client_user)

        response = self.client.post(
            "/api/avis/",
            {
                "demande": self.demande.pk,
                "note": 5,
                "commentaire": "Très bon service et très rapide.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["demande"], self.demande.pk)
        self.assertEqual(response.data["client"], self.client_profile.pk)
        self.assertEqual(response.data["reparateur"], self.reparateur.pk)

    def test_client_ne_peut_pas_creer_avis_sur_demande_non_acceptee(self):
        self.demande.statut = DemandeMiseEnRelation.Statut.EN_ATTENTE
        self.demande.save(update_fields=["statut"])
        self.client.force_authenticate(self.client_user)

        response = self.client.post(
            "/api/avis/",
            {"demande": self.demande.pk, "note": 4, "commentaire": "Pas encore possible."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_client_ne_peut_pas_creer_plusieurs_avis_pour_la_meme_demande(self):
        self.client.force_authenticate(self.client_user)
        self.client.post(
            "/api/avis/",
            {"demande": self.demande.pk, "note": 5, "commentaire": "Premier avis."},
            format="json",
        )

        response = self.client.post(
            "/api/avis/",
            {"demande": self.demande.pk, "note": 4, "commentaire": "Deuxième avis."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_avis_est_visible_dans_les_listes_du_client_et_du_reparateur(self):
        self.client.force_authenticate(self.client_user)
        creation = self.client.post(
            "/api/avis/",
            {"demande": self.demande.pk, "note": 4, "commentaire": "Intervention professionnelle."},
            format="json",
        )
        self.assertEqual(creation.status_code, status.HTTP_201_CREATED)
        self.assertEqual(creation.data["client_nom"], "Avis Client")
        self.assertEqual(creation.data["demande_appareil"], "")

        client_liste = self.client.get("/api/avis/")
        self.assertEqual(client_liste.status_code, status.HTTP_200_OK)
        self.assertEqual(len(client_liste.data["results"]), 1)

        self.client.force_authenticate(self.reparateur_user)
        reparateur_liste = self.client.get("/api/avis/")
        self.assertEqual(reparateur_liste.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reparateur_liste.data["results"]), 1)
        self.assertEqual(reparateur_liste.data["results"][0]["commentaire"], "Intervention professionnelle.")
