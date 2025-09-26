from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    current_app,
    make_response,
)
import random
from helper.utils import user_exists, gen_api_key
from helper.hash import get_user_id_hash
import secrets
from models.table import Api
from extensions import db
from models.table import User, Redirect
from datetime import datetime

user = Blueprint("user", __name__)


def create_userid():
    start = 10**15
    end = (10**16) - 1
    return str(random.randint(start, end))


def create_session(rotate: bool = False):
    """Create or rotate a secure session with random ID + User-Agent binding."""
    if rotate:
        session.clear()  # drop everything before issuing new ID
    session["session_id"] = secrets.token_urlsafe(32)
    session["ua"] = request.headers.get("User-Agent", "")


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


@user.route("/signin", methods=["GET", "POST"])
def signin():
    if validate_session():
        return redirect(url_for("route_bp.routes"))

    if request.method == "POST":
        user_id = create_userid()

        while user_exists(get_user_id_hash(user_id)):
            user_id = create_userid()

        if user_id:
            hashed = get_user_id_hash(user_id)
            user = User(user_id=hashed)
            db.session.add(user)
            db.session.commit()
            # rotate session on signup
            create_session(rotate=True)
            # find the id of the user_id(user_id == password)
            result = User.query.with_entities(User.id).filter_by(user_id=hashed).first()
            """
            Make the session of the id, it is goning to help find the all
            the routes of that perticular id, to show it to profile.html
            """
            session["id"] = result[0]
            return render_template("signin.html", userid=user_id)

    return render_template("signin.html")


@user.route("/login", methods=["GET", "POST"])
def login():

    if validate_session():
        return redirect(url_for("user.profile"))

    if request.method == "POST":
        user_id = request.form.get("userid")
        if user_id and user_exists(get_user_id_hash(user_id)):
            # rotate session on login
            create_session(rotate=True)
            result = (
                User.query.with_entities(User.id)
                .filter_by(user_id=get_user_id_hash(user_id))
                .first()
            )
            session["id"] = result[0]
            return redirect(url_for("route_bp.routes"))
        else:
            return render_template("login.html", error="UserID does not exist.")

    return render_template("login.html")


@user.route("/profile", methods=["GET", "POST"])
def profile():
    action = request.form.get("action")
    if session:
        created_by = session["id"]
    else:
        return redirect(url_for("user.login"))

    # user_table object
    user = User.query.filter_by(id=created_by).first()

    api_keys = [
        row[0]
        for row in Api.query.with_entities(Api.api_key)
        .filter(Api.created_by == session.get("id"))
        .all()
    ]

    if action == "logout":
        session.clear()
        return redirect(url_for("user.login"))

    if action == "gen-api-key":
        # checking if the user already created enough api_keys
        if user.total_api_keys < current_app.config.get("MAX_API_PER_USER", 5):
            # incrementaing to 1
            user.total_api_keys += 1
            # generating
            api_key = gen_api_key()
            # hashing
            hash_api = get_user_id_hash(api_key)
            # adding to api_table
            api = Api(api_key=hash_api, created_by=created_by)
            # commiting change in bot api_table and user_table
            # db.session.add(user)
            db.session.add(api)
            db.session.commit()
        else:
            return render_template(
                "profile.html",
                api_keys=api_keys,
                error=f"You can create up to {current_app.config.get('MAX_API_PER_USER', 5)} API keys in total.",
            )
        db.session.commit()
        return render_template("profile.html", api_key=api_key)

    if request.form.get("delete_api"):
        api_key = request.form.get("delete_api")
        api = Api.query.filter_by(api_key=api_key, created_by=created_by).first()
        if not api:
            return render_template(
                "profile.html",
                api_key=api_key,
                error="API key does not exist or you don't own it.",
            )
        db.session.delete(api)
        user.total_api_keys -= 1
        db.session.commit()
        return redirect(url_for("user.profile"))

    return render_template(
        "profile.html",
        session=session.get("session_id"),
        api_keys=api_keys,
    )


@user.route("/settings", methods=["GET"])
def settings():
    if request.args.get("settings") == "save":
        theme = request.args.get("theme", "auto")
        limit = request.args.get(
            "limit", current_app.config.get("ROUTE_PAGE_LIMIT"), type=int
        )

        resp = make_response(redirect(url_for("user.settings")))
        resp.set_cookie(
            "theme",
            theme,
            max_age=current_app.config.get("COOKIE_AGE", (60 * 60 * 24) * 14),
        )
        resp.set_cookie(
            "limit",
            str(limit),
            max_age=current_app.config.get("COOKIE_AGE", (60 * 60 * 24) * 14),
        )
        return resp
    theme = request.cookies.get("theme")
    limit = request.cookies.get("limit")

    return render_template("settings.html", theme=theme, limit=limit)
