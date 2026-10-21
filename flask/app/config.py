import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sesión (cookie firmada que guarda el access token de Auth0)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

    BEHIND_PROXY = os.environ.get("BEHIND_PROXY", "0") == "1"

    # Auth0
    AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
    AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")
    AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
    AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET", "")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "")
    AUTH0_DOMAIN = "test-tenant.us.auth0.com"
    AUTH0_AUDIENCE = "todoapp-api"
    AUTH0_CLIENT_ID = "test-client-id"
    AUTH0_CLIENT_SECRET = "test-client-secret"