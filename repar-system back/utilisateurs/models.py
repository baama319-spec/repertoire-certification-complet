from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UtilisateurManager(BaseUserManager):
    """Gestionnaire cohérent avec l'e-mail comme identifiant de connexion."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'adresse e-mail est obligatoire.")
        utilisateur = self.model(email=self.normalize_email(email), **extra_fields)
        utilisateur.set_password(password)
        utilisateur.save(using=self._db)
        return utilisateur

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", Utilisateur.Role.CLIENT)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Utilisateur.Role.ADMINISTRATEUR)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superutilisateur doit avoir les droits administrateur Django.")
        return self._create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = "CLIENT", "Client"
        REPARATEUR = "REPARATEUR", "Réparateur"
        ADMINISTRATEUR = "ADMINISTRATEUR", "Administrateur"
    username = models.CharField(max_length=150, blank=True)
    nom = models.CharField(max_length=150)
    prenom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=30, blank=True)
    # Une image commune est créée dès l'inscription. Elle garantit que chaque
    # compte a un avatar affichable, même avant son premier téléversement.
    photo_profil = models.ImageField(upload_to="profils/", default="profils/avatar-defaut.svg")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    actif = models.BooleanField(default=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]
    objects = UtilisateurManager()
    def __str__(self):
        return f"{self.prenom} {self.nom}"
