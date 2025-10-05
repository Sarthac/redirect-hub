import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    PROJECT_NAME = "redirect-hub"
    DATABASE_NANE = "database.db"
    FORBIDEN_ROUTES = [
        "home",
        "register",
        "signin",
        "signup",
        "signout",
        "login",
        "logout",
        "profile",
        "account",
        "user",
        "about",
        "setting",
        "settings",
        "api",
        "github",
        "tor",
        "i2p",
    ]

    LINKS = {
        "tor": "http://ylmkenmpxk7dpcv5seu4kaom5e2ulhnieylpgvafj27wgocdwyx4n6ad.onion",
        "i2p": "http://vgit4qh3acgqrg6fc4o4tiezef22yfmmvpjsd4nn7lztvw3z3lwa.b32.i2p",
        "github": "https://github.com/sarthac/redirect-hub",
    }

    GENERATE_ROUTE_LENGTH = 5
    ROUTE_GENERATE_LIMIT = 5
    API_KEY_LENGTH = 32
    ROUTE_PAGE_LIMIT = 20
    MAX_API_PER_USER = 5

    HOST = "0.0.0.0"
    PORT = 5002
    COOKIE_AGE = (60 * 60 * 24) * 14

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # session config
    SECRET_KEY = os.environ["SECRET_KEY"]
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True  # session ends when browser closes
    SESSION_USE_SIGNER = True  # sign the session ID cookie
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from reading cookies
    SESSION_COOKIE_SAMESITE = "Lax"  # Mitigates CSRF (cross-site request forgery)


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_NAME = "dev_database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_NAME}"


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_NAME = "database.db"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_NAME}"
    SESSION_COOKIE_SECURE = True
