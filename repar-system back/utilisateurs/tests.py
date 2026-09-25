from django.urls import reverse
from rest_framework.test import APITestCase
from clients.models import Client
from utilisateurs.models import Utilisateur


class AuthentificationTests(APITestCase):
    def test_inscription_puis_connexion(self):
        inscription = self.client.post(reverse("utilisateur-inscription"), {
            "prenom": "Awa", "nom": "Diop", "email": "awa@example.sn",
            "telephone": "+221770000000", "password": "motdepasse-solide",
        }, format="json")

        self.assertEqual(inscription.status_code, 201)
        self.assertIn("token", inscription.data)
        self.assertNotIn("password", inscription.data["utilisateur"])
        self.assertTrue(Client.objects.filter(utilisateur__email="awa@example.sn").exists())

        connexion = self.client.post(reverse("utilisateur-connexion"), {
            "email": "awa@example.sn", "password": "motdepasse-solide",
        }, format="json")

        self.assertEqual(connexion.status_code, 200)
        self.assertIn("token", connexion.data)
        self.assertEqual(connexion.data["utilisateur"]["email"], "awa@example.sn")

    def test_un_utilisateur_ne_peut_pas_lire_les_autres_comptes(self):
        self.client.post(reverse("utilisateur-inscription"), {
            "prenom": "Awa", "nom": "Diop", "email": "awa@example.sn", "password": "motdepasse-solide",
        }, format="json")
        connexion = self.client.post(reverse("utilisateur-connexion"), {
            "email": "awa@example.sn", "password": "motdepasse-solide",
        }, format="json")

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {connexion.data['token']}")
        self.assertEqual(self.client.get(reverse("utilisateur-list")).status_code, 403)

    def test_un_administrateur_est_redirigeable_et_peut_lister_les_comptes(self):
        administrateur = Utilisateur.objects.create_user(
            email="admin@reparsystem.sn", password="motdepasse-solide",
            prenom="Admin", nom="System", role=Utilisateur.Role.ADMINISTRATEUR,
        )
        connexion = self.client.post(reverse("utilisateur-connexion"), {
            "email": administrateur.email, "password": "motdepasse-solide",
        }, format="json")

        self.assertEqual(connexion.status_code, 200)
        self.assertEqual(connexion.data["utilisateur"]["role"], Utilisateur.Role.ADMINISTRATEUR)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {connexion.data['token']}")
        self.assertEqual(self.client.get(reverse("utilisateur-list")).status_code, 200)
