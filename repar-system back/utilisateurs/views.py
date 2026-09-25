from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from .models import Utilisateur
from .serializers import InscriptionSerializer, UtilisateurSerializer
from commun.permissions import EstAdministrateur

class UtilisateurViewSet(ModelViewSet):
    queryset = Utilisateur.objects.all().order_by("-date_inscription")
    serializer_class = UtilisateurSerializer

    def get_permissions(self):
        if self.action in ("inscription", "connexion"):
            return [AllowAny()]
        if self.action in ("list", "destroy"):
            return [EstAdministrateur()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        return InscriptionSerializer if self.action == "inscription" else UtilisateurSerializer

    def get_queryset(self):
        if self.request.user.role == Utilisateur.Role.ADMINISTRATEUR:
            return super().get_queryset()
        return super().get_queryset().filter(pk=self.request.user.pk)

    @action(detail=False, methods=["post"])
    def inscription(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        utilisateur = serializer.save()
        token, _ = Token.objects.get_or_create(user=utilisateur)
        return Response({
            "token": token.key,
            "utilisateur": UtilisateurSerializer(utilisateur).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def connexion(self, request):
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")
        utilisateur = authenticate(request, username=email, password=password)
        if not utilisateur or not utilisateur.actif:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_400_BAD_REQUEST)
        token, _ = Token.objects.get_or_create(user=utilisateur)
        return Response({"token": token.key, "utilisateur": UtilisateurSerializer(utilisateur).data})

    @action(detail=False, methods=["get"])
    def moi(self, request):
        """Retourne l'utilisateur de la session identifiée par le token."""
        return Response(UtilisateurSerializer(request.user).data)

    @action(detail=False, methods=["post"])
    def changer_mot_de_passe(self, request):
        """Change le mot de passe après vérification de l'ancien secret."""
        actuel = request.data.get("mot_de_passe_actuel", "")
        nouveau = request.data.get("nouveau_mot_de_passe", "")
        confirmation = request.data.get("confirmation_mot_de_passe", "")
        if not request.user.check_password(actuel):
            return Response({"mot_de_passe_actuel": ["Le mot de passe actuel est incorrect."]}, status=status.HTTP_400_BAD_REQUEST)
        if len(nouveau) < 8:
            return Response({"nouveau_mot_de_passe": ["Le nouveau mot de passe doit contenir au moins 8 caractères."]}, status=status.HTTP_400_BAD_REQUEST)
        if nouveau != confirmation:
            return Response({"confirmation_mot_de_passe": ["Les mots de passe ne correspondent pas."]}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(nouveau)
        request.user.save(update_fields=["password"])
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        return Response({"detail": "Mot de passe modifié.", "token": token.key})

    @action(detail=False, methods=["post"])
    def deconnexion(self, request):
        """Invalide le token actuel, y compris si le client l'a conservé."""
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
