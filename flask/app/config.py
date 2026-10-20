import os

from dotnev import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://jorge:jorgeGenialsixseven67@db:5432/lacartados")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me-32-bytes-min")
    JWT_EXPIRES_MINUTES = int(os.environ.get("JWT_EXPIRES_MINUTES", "60"))
    JWT_ISSUER = os.environ.get("JWT_ISSUER", "flask-todoapp")

class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = "postgresql://jorge:jorgeGenialsixseven67@db:5432/lacartados"
    JWT_SECRET_KEY = "test-jwt-secret-with-at-least-32-bytes"
    JWT_EXPIRES_MINUTES = 5