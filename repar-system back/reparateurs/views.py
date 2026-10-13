from math import asin, cos, radians, sin, sqrt

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from django.utils import timezone
from django.db.models import Avg, Count
from utilisateurs.models import Utilisateur
from .models import Reparateur, ReparateurDocument
from .serializers import ReparateurSerializer


class ReparateurViewSet(ModelViewSet):
    queryset = Reparateur.objects.select_related("utilisateur").prefetch_related("specialites", "zones_intervention").annotate(note_moyenne=Avg("avis__note"), nombre_avis=Count("avis", distinct=True)); serializer_class = ReparateurSerializer
    def get_permissions(self):
        return [AllowAny()] if self.action in ("list", "retrieve") else [IsAuthenticated()]

    @staticmethod
    def _distance(reparateur, latitude, longitude):
        distances = []
        if reparateur.latitude is None or reparateur.longitude is None:
            return None
        for zone_latitude, zone_longitude in [(reparateur.latitude, reparateur.longitude)]:
            p1, p2 = radians(latitude), radians(float(zone_latitude))
            dlat = radians(float(zone_latitude) - latitude)
            dlon = radians(float(zone_longitude) - longitude)
            value = sin(dlat / 2) ** 2 + cos(p1) * cos(p2) * sin(dlon / 2) ** 2
            distances.append(6371 * 2 * asin(sqrt(value)))
        return min(distances) if distances else None

    def list(self, request, *args, **kwargs):
        queryset = list(self.filter_queryset(self.get_queryset()))
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            latitude = longitude = None
        distances = {item.pk: self._distance(item, latitude, longitude) for item in queryset} if latitude is not None else {}
        if distances:
            queryset.sort(key=lambda item: distances[item.pk] if distances[item.pk] is not None else float("inf"))
        page = self.paginate_queryset(queryset)
        items = page if page is not None else queryset
        data = [self.get_serializer(item, context={"distance_km": distances.get(item.pk)}).data for item in items]
        return self.get_paginated_response(data) if page is not None else Response(data)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ("list", "retrieve"):
            if self.request.user.is_authenticated and self.request.user.role == Utilisateur.Role.ADMINISTRATEUR:
                return queryset
            return queryset.filter(
                statut_verification=Reparateur.StatutVerification.VALIDEE,
                utilisateur__actif=True,
            ).order_by("-date_verification", "-pk")
        if self.request.user.role == Utilisateur.Role.ADMINISTRATEUR:
            return queryset
        return queryset.filter(utilisateur=self.request.user)

    @action(detail=False, methods=["get", "patch"])
    def moi(self, request):
        try:
            profil = Reparateur.objects.get(utilisateur=request.user)
        except Reparateur.DoesNotExist:
            return Response({"detail": "Aucun profil professionnel."}, status=404)
        if request.method == "PATCH":
            serializer = self.get_serializer(profil, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(profil).data)

    @action(detail=False, methods=["get"])
    def recommandations(self, request):
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response({"detail": "La latitude et la longitude sont obligatoires."}, status=400)

        queryset = self.queryset.filter(
            statut_verification=Reparateur.StatutVerification.VALIDEE,
            utilisateur__actif=True,
            latitude__isnull=False,
            longitude__isnull=False,
        )
        specialite = request.query_params.get("specialite")
        if specialite:
            queryset = queryset.filter(specialites__id=specialite)
        queryset = list(queryset.distinct())
        distances = {item.pk: self._distance(item, latitude, longitude) for item in queryset}
        queryset.sort(key=lambda item: distances[item.pk] if distances[item.pk] is not None else float("inf"))
        return Response([
            self.get_serializer(item, context={"distance_km": distances[item.pk]}).data
            for item in queryset[:10]
        ])

    @action(detail=False, methods=["get", "post", "patch"])
    def candidature(self, request):
        """Une candidature est un profil réparateur rattaché au compte courant.

        Le rôle Client n'est pas remplacé : un même utilisateur peut donc garder
        ses demandes client et déposer sa candidature professionnelle.
        """
        profil = Reparateur.objects.filter(utilisateur=request.user).first()
        if request.method == "GET":
            if not profil:
                return Response({"profil": None})
            return Response({"profil": self.get_serializer(profil).data})
        if profil and profil.statut_verification != Reparateur.StatutVerification.REFUSEE:
            return Response({"detail": "Une candidature est déjà en cours ou vérifiée."}, status=status.HTTP_409_CONFLICT)

        photo_carte = request.FILES.get("photo_carte_identite") or request.data.get("photo_carte_identite")
        if not profil and not photo_carte:
            return Response({"photo_carte_identite": ["Une photo de la carte d’identité est obligatoire."]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(profil, data=request.data, partial=bool(profil))
        serializer.is_valid(raise_exception=True)
        creation = profil is None
        profil = serializer.save(utilisateur=request.user) if creation else serializer.save(
            statut_verification=Reparateur.StatutVerification.EN_ATTENTE, motif_refus="", profil_verifie=False
        )

        if "photo_carte_identite" in request.FILES:
            profil.photo_carte_identite = request.FILES["photo_carte_identite"]
            profil.save(update_fields=("photo_carte_identite",))

        documents = request.FILES.getlist("documents")
        if documents:
            document_types = request.POST.getlist("document_types")
            for index, fichier in enumerate(documents):
                type_document = document_types[index] if index < len(document_types) and document_types[index].strip() else "AUTRE"
                ReparateurDocument.objects.create(reparateur=profil, type_document=type_document, document=fichier)

        return Response({"profil": self.get_serializer(profil).data}, status=status.HTTP_201_CREATED if creation else status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def verifier(self, request, pk=None):
        if request.user.role != Utilisateur.Role.ADMINISTRATEUR:
            raise PermissionDenied("Seul un administrateur peut valider une candidature.")
        reparateur = self.get_object()
        statut = request.data.get("statut_verification")
        if statut not in (Reparateur.StatutVerification.VALIDEE, Reparateur.StatutVerification.REFUSEE):
            return Response({"statut_verification": ["Choisissez VALIDEE ou REFUSEE."]}, status=status.HTTP_400_BAD_REQUEST)
        reparateur.statut_verification = statut
        reparateur.profil_verifie = False
        reparateur.motif_refus = "" if statut == Reparateur.StatutVerification.VALIDEE else request.data.get("motif_refus", "").strip()
        reparateur.date_verification = timezone.now() if statut == Reparateur.StatutVerification.VALIDEE else None
        reparateur.save(update_fields=("statut_verification", "profil_verifie", "motif_refus", "date_verification"))
        return Response(self.get_serializer(reparateur).data)

    @action(detail=True, methods=["post"])
    def certifier_pro(self, request, pk=None):
        if request.user.role != Utilisateur.Role.ADMINISTRATEUR:
            raise PermissionDenied("Seul un administrateur peut certifier un réparateur.")
        reparateur = self.get_object()
        if reparateur.statut_verification != Reparateur.StatutVerification.VALIDEE:
            return Response({"detail": "La candidature doit être validée avant certification."}, status=status.HTTP_409_CONFLICT)
        reparateur.profil_verifie = True
        reparateur.date_verification = timezone.now()
        reparateur.save(update_fields=("profil_verifie", "date_verification"))
        return Response(self.get_serializer(reparateur).data)

    @action(detail=True, methods=["post"])
    def bloquer(self, request, pk=None):
        """Bloque ou réactive le compte professionnel et invalide sa session."""
        if request.user.role != Utilisateur.Role.ADMINISTRATEUR:
            raise PermissionDenied("Seul un administrateur peut bloquer un réparateur.")
        reparateur = self.get_object()
        utilisateur = reparateur.utilisateur
        bloquer = request.data.get("bloquer", True)
        if not isinstance(bloquer, bool):
            return Response({"bloquer": ["La valeur doit être booléenne."]}, status=status.HTTP_400_BAD_REQUEST)
        if utilisateur == request.user and bloquer:
            return Response({"detail": "Vous ne pouvez pas bloquer votre propre compte."}, status=status.HTTP_400_BAD_REQUEST)
        utilisateur.actif = not bloquer
        utilisateur.save(update_fields=("actif",))
        if bloquer:
            Token.objects.filter(user=utilisateur).delete()
        return Response(self.get_serializer(reparateur).data)
