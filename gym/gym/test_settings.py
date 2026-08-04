from .settings import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
WRITE_DB_INSTRUMENTATION_ENABLED = False

MIGRATION_MODULES = {
    "administracion": None,
    "entrada": None,
    "finanzas": None,
    "home": None,
    "rehabilitacion": None,
    "usuarios": None,
}
