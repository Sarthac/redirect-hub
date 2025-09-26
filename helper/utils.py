import validators
from flask import session, request, current_app
import secrets
from extensions import db
from models.table import User


def forbiden_words(route: str) -> bool:
    list_of_routes = ["home", "signin", "login", "profile", "settings", "api", "github"]
    return route in list_of_routes


def user_exists(user_id: str) -> bool:
    existing_user = (
        User.query.with_entities(User.user_id).filter_by(user_id=user_id).first()
    )
    print(existing_user)
    return existing_user != None


def is_valid_url(url: str) -> bool:
    return validators.url(url) is True


def gen_api_key():
    return secrets.token_hex(current_app.config.get("API_KEY_LENGTH", 16))


def generate_route():
    import random
    import string

    chars = string.ascii_letters + string.digits
    length = current_app.config.get("GENERATE_ROUTE_LENGTH", 6)

    return "".join(random.choices(chars, k=length))


def validate_session() -> bool:
    """Validate session by checking stored UA + session_id exists"""
    current_ua = request.headers.get("User-Agent", "")
    stored_ua = session.get("ua")
    sid = session.get("session_id")

    if not sid or not stored_ua:
        return False

    if current_ua != stored_ua:
        session.clear()
        return False

    return True
