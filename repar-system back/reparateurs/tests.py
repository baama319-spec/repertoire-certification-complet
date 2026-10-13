from django.core.files.uploadedfile import SimpleUploadedFile
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
            statut_verification=Reparateur.StatutVerification.VALIDEE,
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

    def test_reparateur_en_attente_napparait_pas_dans_lannuaire_ou_les_recommandations(self):
        candidat = Utilisateur.objects.create_user(
            email="candidat-en-attente@example.test", password="motdepasse", nom="Candidat", prenom="Test",
        )
        profil = Reparateur.objects.create(utilisateur=candidat, latitude=14.7167, longitude=-17.4677)
        self.client.force_authenticate(candidat)

        annuaire = self.client.get(reverse("reparateur-list"))
        recommandations = self.client.get(
            reverse("reparateur-recommandations"),
            {"latitude": 14.72, "longitude": -17.46},
        )
        fiche = self.client.get(reverse("reparateur-detail", args=[profil.pk]))

        self.assertEqual(annuaire.status_code, 200)
        self.assertNotIn(profil.pk, [item["id"] for item in annuaire.data.get("results", annuaire.data)])
        self.assertEqual(recommandations.status_code, 200)
        self.assertNotIn(profil.pk, [item["id"] for item in recommandations.data])
        self.assertEqual(fiche.status_code, 404)


class CandidatureReparateurTests(APITestCase):
    def test_profil_napparait_dans_lannuaire_quapres_validation_admin(self):
        admin = Utilisateur.objects.create_user(
            email="admin-validation@example.test", password="motdepasse", nom="Admin", prenom="Test",
            role=Utilisateur.Role.ADMINISTRATEUR,
        )
        candidat = Utilisateur.objects.create_user(
            email="candidat-annuaire@example.test", password="motdepasse", nom="Candidat", prenom="Test",
        )
        profil = Reparateur.objects.create(utilisateur=candidat)
        url = reverse("reparateur-list")

        avant_validation = self.client.get(url)
        self.assertNotIn(profil.pk, [item["id"] for item in avant_validation.data.get("results", avant_validation.data)])

        self.client.force_authenticate(admin)
        validation = self.client.post(
            reverse("reparateur-verifier", args=[profil.pk]),
            {"statut_verification": Reparateur.StatutVerification.VALIDEE},
            format="json",
        )
        self.assertEqual(validation.status_code, 200)

        candidat = Utilisateur.objects.get(pk=candidat.pk)
        self.client.force_authenticate(candidat)
        compte_actualise = self.client.get(reverse("utilisateur-moi"))
        self.assertEqual(compte_actualise.status_code, 200)
        self.assertEqual(compte_actualise.data["profil_reparateur"]["statut_verification"], Reparateur.StatutVerification.VALIDEE)
        self.assertEqual(compte_actualise.data["role"], Utilisateur.Role.CLIENT)

        self.client.force_authenticate(None)
        apres_validation = self.client.get(url)
        self.assertIn(profil.pk, [item["id"] for item in apres_validation.data.get("results", apres_validation.data)])

    def test_candidature_exige_une_photo_carte_identite_et_accepte_des_documents(self):
        utilisateur = Utilisateur.objects.create_user(
            email="candidat@example.test", password="motdepasse", nom="Candidat", prenom="Test",
        )
        self.client.force_authenticate(utilisateur)

        carte = SimpleUploadedFile("carte-identite.png", b"fake-image-content", content_type="image/png")
        document = SimpleUploadedFile("diplome.pdf", b"fake-pdf-content", content_type="application/pdf")

        response = self.client.post(
            reverse("reparateur-candidature"),
            {
                "description": "Je suis réparateur depuis 7 ans et je traite smartphones et tablettes.",
                "annee_experience": 7,
                "photo_carte_identite": carte,
                "documents": [document],
                "document_types": ["DIPLOME"],
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201, response.data)
        self.assertTrue(response.data["profil"]["photo_carte_identite"])
        self.assertEqual(len(response.data["profil"]["documents_detail"]), 1)
        self.assertEqual(response.data["profil"]["documents_detail"][0]["type_document"], "DIPLOME")
