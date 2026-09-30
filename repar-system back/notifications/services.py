import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def envoyer_notification_n8n(user, title, message, event_type):
    payload = {
        "user_id": user.id,
        "user_email": user.email,
        "event_type": event_type,
        "title": title,
        "message": message,
    }

    try:
        response = requests.post(
            settings.N8N_NOTIFICATION_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as error:
        # L'échec de l'e-mail ne doit pas empêcher la réponse métier, mais il doit
        # être visible dans la console / les logs Django.
        logger.exception("Échec de l'appel au webhook n8n : %s", error)
        return False
