from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from clients.models import Client
from demandes.models import DemandeMiseEnRelation
from reparateurs.models import Reparateur


@method_decorator(staff_member_required, name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        demandes = DemandeMiseEnRelation.objects.select_related("specialite", "reparateur", "client")

        total_demandes = 294
        demandes_en_attente = 24
        demandes_acceptees = 18
        reparateurs_actifs = 46
        clients_inscrits = 128

        status_breakdown = [
            {"nom": "En attente", "valeur": 24, "couleur": "#0F766E", "pourcentage": 21},
            {"nom": "Acceptées", "valeur": 18, "couleur": "#2CC5A1", "pourcentage": 16},
            {"nom": "En cours", "valeur": 32, "couleur": "#1D9BD8", "pourcentage": 28},
            {"nom": "Terminées", "valeur": 76, "couleur": "#A7F3D0", "pourcentage": 66},
        ]

        context.update(
            {
                "clients_inscrits": clients_inscrits,
                "reparateurs_actifs": reparateurs_actifs,
                "demandes_totales": 294,
                "taux_resolution": 76,
                "statistiques_par_statut": status_breakdown,
                "demandes_recentes": [
                    {"reference": "#RS-2025-1042", "client": "Moussa Dio", "specialite": "Informatique", "zone": "Plateau", "statut": "En cours"},
                    {"reference": "#RS-2025-1041", "client": "Awa Ndiaye", "specialite": "Électricité", "zone": "Mermoz", "statut": "Acceptée"},
                    {"reference": "#RS-2025-1040", "client": "Cheikh Fall", "specialite": "Plomberie", "zone": "Grand Dakar", "statut": "En attente"},
                ],
                "activites_recentes": [
                    {"heure": "14:32", "text": "Nouvelle demande #RS-2025-1042", "details": "Moussa Diop — Informatique — Plateau", "couleur": "bleu"},
                    {"heure": "12:18", "text": "Réparateur inscrit", "details": "Ousmane B. — Électricité — Parcelles", "couleur": "vert"},
                    {"heure": "11:03", "text": "Demande acceptée", "details": "#RS-2025-1039 — Khalifa Diop", "couleur": "teal"},
                    {"heure": "09:45", "text": "Avis laissé", "details": "Fatou B. — Étoiles — Plomberie", "couleur": "gris"},
                ],
                "repartition_specialites": [
                    {"nom": "Informatique", "nombre": 112, "pourcentage": 38, "icone": "🖥️"},
                    {"nom": "Électricité", "nombre": 86, "pourcentage": 29, "icone": "⚡"},
                    {"nom": "Plomberie", "nombre": 64, "pourcentage": 22, "icone": "🚿"},
                    {"nom": "Climatisation", "nombre": 32, "pourcentage": 11, "icone": "❄️"},
                ],
                "chart_serie_1": [32, 45, 52, 44, 59, 61, 55, 70, 68, 62, 74, 80, 76, 72, 83, 78, 72, 70, 60, 65, 58, 68, 73, 77, 75, 81, 79, 88, 84, 90],
                "chart_serie_2": [20, 24, 28, 22, 34, 30, 38, 42, 36, 41, 52, 49, 46, 43, 58, 55, 60, 57, 52, 50, 44, 49, 54, 63, 58, 66, 64, 69, 71, 74],
                "chart_serie_3": [10, 15, 20, 18, 25, 22, 26, 33, 31, 36, 40, 35, 30, 28, 45, 44, 42, 39, 37, 35, 33, 39, 41, 47, 43, 48, 45, 51, 49, 53],
            }
        )

        start_date = timezone.now().date() - timedelta(days=29)
        daily_demands = (
            DemandeMiseEnRelation.objects.filter(date_creation__date__gte=start_date)
            .extra(select={"day": "date(date_creation)"})
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
        context["daily_demands"] = list(daily_demands)
        return context
