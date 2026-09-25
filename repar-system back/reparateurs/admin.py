from django.contrib import admin, messages
from django.utils import timezone

from .models import Reparateur


@admin.register(Reparateur)
class ReparateurAdmin(admin.ModelAdmin):
    """Administration des profils et candidatures professionnels."""

    list_display = (
        "nom_complet", "email", "statut_verification", "profil_verifie",
        "annee_experience", "date_verification",
    )
    list_filter = ("statut_verification", "profil_verifie", "specialites")
    search_fields = ("utilisateur__nom", "utilisateur__prenom", "utilisateur__email")
    filter_horizontal = ("specialites", "zones_intervention")
    readonly_fields = ("date_verification",)
    fields = (
        "utilisateur", "description", "annee_experience", "specialites",
        "zones_intervention", "statut_verification", "motif_refus",
        "profil_verifie", "date_verification",
    )
    actions = ("valider_candidatures", "certifier_profils", "refuser_candidatures")

    @admin.display(description="Réparateur", ordering="utilisateur__nom")
    def nom_complet(self, reparateur):
        return f"{reparateur.utilisateur.prenom} {reparateur.utilisateur.nom}"

    @admin.display(description="E-mail", ordering="utilisateur__email")
    def email(self, reparateur):
        return reparateur.utilisateur.email

    @admin.action(description="Valider les candidatures sélectionnées")
    def valider_candidatures(self, request, queryset):
        nombre = queryset.update(
            statut_verification=Reparateur.StatutVerification.VALIDEE,
            profil_verifie=False,
            motif_refus="",
            date_verification=timezone.now(),
        )
        self.message_user(request, f"{nombre} candidature(s) validée(s), sans certification Pro.", messages.SUCCESS)

    @admin.action(description="Certifier Pro les profils sélectionnés")
    def certifier_profils(self, request, queryset):
        nombre = queryset.filter(statut_verification=Reparateur.StatutVerification.VALIDEE).update(profil_verifie=True, date_verification=timezone.now())
        self.message_user(request, f"{nombre} profil(s) certifié(s) Pro.", messages.SUCCESS)

    @admin.action(description="Refuser les candidatures sélectionnées")
    def refuser_candidatures(self, request, queryset):
        nombre = queryset.update(
            statut_verification=Reparateur.StatutVerification.REFUSEE,
            profil_verifie=False,
            date_verification=None,
        )
        self.message_user(request, f"{nombre} candidature(s) marquée(s) comme refusée(s). Ajoutez le motif dans chaque fiche.", messages.WARNING)
