import os


class Config:
    PROJECT_NAME = "Unknown"
    DATABASE_NANE = "database.db"
    forbiden_routes = ["signin", "login", "profile"]
    GENERATE_ROUTE_LENGTH = 5
    ROUTE_GENERATE_LIMIT = 5
    API_KEY_LENGTH = 32
    ROUTE_PAGE_LIMIT = 20

    HOST = "0.0.0.0"
    PORT = 5002
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # session config
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True  # session ends when browser closes
    SESSION_USE_SIGNER = True  # sign the session ID cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from reading cookies
    SESSION_COOKIE_SAMESITE = "Lax"  # Mitigates CSRF (cross-site request forgery)


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = "dev_database.db"

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_NAME}"

    # SQLALCHEMY_DATABASE_URI = (
    #     f"sqlite:///{os.path.join(Config.BASE_DIR, DATABASE_NAME)}"
    # )


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_NAME = "database.db"
    SESSION_COOKIE_SECURE = True

    # SQLALCHEMY_DATABASE_URI = (
    #     f"sqlite:///{os.path.join(Config.BASE_DIR, DATABASE_NAME)}"
    # )
