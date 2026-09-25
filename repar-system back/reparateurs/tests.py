from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from utilisateurs.models import Utilisateur
from specialites.models import Specialite
from .models import Reparateur


class BlocageReparateurTests(APITestCase):
    def setUp(self):
        self.admin = Utilisateur.objects.create_user(
            email="admin@example.test", password="motdepasse", nom="Admin", prenom="Test",
            role=Utilisateur.Role.ADMINISTRATEUR,
        )
        self.utilisateur = Utilisateur.objects.create_user(
            email="pro@example.test", password="motdepasse", nom="Pro", prenom="Test",
        )
        self.reparateur = Reparateur.objects.create(utilisateur=self.utilisateur)
        self.token = Token.objects.create(user=self.utilisateur)
        self.client.force_authenticate(self.admin)

    def test_administrateur_peut_bloquer_et_debloquer_un_reparateur(self):
        url = reverse("reparateur-bloquer", args=[self.reparateur.pk])

        response = self.client.post(url, {"bloquer": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.utilisateur.refresh_from_db()
        self.assertFalse(self.utilisateur.actif)
        self.assertFalse(Token.objects.filter(pk=self.token.pk).exists())

        response = self.client.post(url, {"bloquer": False}, format="json")
        self.assertEqual(response.status_code, 200)
        self.utilisateur.refresh_from_db()
        self.assertTrue(self.utilisateur.actif)


class RecommandationsReparateurTests(APITestCase):
    def test_client_recoit_les_reparateurs_verifies_par_distance(self):
        client = Utilisateur.objects.create_user(
            email="client@example.test", password="motdepasse", nom="Client", prenom="Test",
        )
        pro_user = Utilisateur.objects.create_user(
            email="pro-reco@example.test", password="motdepasse", nom="Pro", prenom="Proche",
        )
        specialite, _ = Specialite.objects.get_or_create(nom="Réparation de smartphones")
        pro = Reparateur.objects.create(
            utilisateur=pro_user,
            latitude=14.7167,
            longitude=-17.4677,
            profil_verifie=True,
        )
        pro.specialites.add(specialite)
        self.client.force_authenticate(client)

        response = self.client.get(
            reverse("reparateur-recommandations"),
            {"latitude": 14.72, "longitude": -17.46, "specialite": specialite.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], pro.pk)
        self.assertIsNotNone(response.data[0]["distance_km"])
