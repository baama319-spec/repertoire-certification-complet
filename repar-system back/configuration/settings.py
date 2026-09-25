from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def charger_fichier_env():
    fichier_env = BASE_DIR / ".env"
    if not fichier_env.exists():
        return
    for ligne in fichier_env.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        valeur = valeur.strip().strip("\"'")
        os.environ.setdefault(cle.strip(), valeur)


charger_fichier_env()
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-this-development-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [host for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "rest_framework", "rest_framework.authtoken", "utilisateurs", "reparateurs", "clients", "demandes",
    "specialites", "localisations", "realisations", "avis", "notifications", "diagnostics",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "configuration.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True,
              "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
              "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "configuration.wsgi.application"
ASGI_APPLICATION = "configuration.asgi.application"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE, TIME_ZONE, USE_I18N, USE_TZ = "fr", "Africa/Dakar", True, True
STATIC_URL, MEDIA_URL = "/static/", "/media/"
STATIC_ROOT, MEDIA_ROOT = BASE_DIR / "staticfiles", BASE_DIR / "medias"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "utilisateurs.Utilisateur"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
    "DEFAULT_PAGINATION_CLASS": "commun.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
}
