import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]   # sin valor por defecto
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me-32-bytes-min")
    JWT_EXPIRES_MINUTES = int(os.environ.get("JWT_EXPIRES_MINUTES", "60"))
    JWT_ISSUER = os.environ.get("JWT_ISSUER", "flask-todoapp")


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    # Una base de pruebas separada (ej. lacartados_test), nunca la real
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "")
    JWT_SECRET_KEY = "test-jwt-secret-with-at-least-32-bytes"
    JWT_EXPIRES_MINUTES = 5