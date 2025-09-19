from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    current_app,
)
import random
from helper.utils import user_exists, is_valid_url, gen_api_key
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
        return redirect(url_for("user.profile"))

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
            return redirect(url_for("user.profile"))
        else:
            return render_template("login.html", error="UserID does not exist.")

    return render_template("login.html")


@user.route("/profile", methods=["GET", "POST"])
def profile():
    if not validate_session():
        return redirect(url_for("user.login"))

    # if request.method == "GET":
    page = request.args.get("page", 1, type=int)
    limit = request.args.get(
        "limit", current_app.config.get("ROUTE_PAGE_LIMIT", 20), type=int
    )

    results = (
        Redirect.query.filter_by(created_by=session["id"])
        .order_by(Redirect.created_at.asc())
        .paginate(page=page, per_page=limit, max_per_page=50, error_out=False)
    )

    api_keys = [
        row[0]
        for row in Api.query.with_entities(Api.api_key)
        .filter(Api.created_by == session.get("id"))
        .all()
    ]

    if request.method == "POST":
        route = request.form.get("route")
        url = request.form.get("url")
        action = request.form.get("action")
        created_by = session["id"]

        if action == "edit" and url:
            # checking if url is valid
            if not is_valid_url(url):
                return render_template(
                    "profile.html",
                    session=session.get("session_id"),
                    results=results,
                    api_keys=api_keys,
                    error="URL is not valid",
                    limit=limit,
                )
                # return url_for("user.profile", error="URL is not valid")
            new_url = Redirect.query.filter(
                (Redirect.route == route) & (Redirect.created_by == created_by)
            ).first()
            if new_url:
                new_url.url = url
                new_url.updated_at = datetime.now()
                db.session.commit()
                return render_template(
                    "profile.html",
                    results=results,
                    api_keys=api_keys,
                    limit=limit,
                    message="Success, URL Updated.",
                )

        if action == "logout":
            session.clear()
            return redirect(url_for("user.login"))

        if action == "gen-api-key":
            api_key = gen_api_key()
            print(api_key)
            hash_api = get_user_id_hash(api_key)
            api = Api(api_key=hash_api, created_by=created_by)
            db.session.add(api)
            db.session.commit()
            return render_template("profile.html", api_key=api_key)

    return render_template(
        "profile.html",
        session=session.get("session_id"),
        results=results,
        api_keys=api_keys,
        limit=limit,
    )
