from flask import g, Blueprint, request, render_template, session, current_app
import sqlite3
from helper.utils import forbiden_words, is_valid_url, generate_route
from extensions import db
from models.table import Redirect

home = Blueprint("home", __name__)


def get_db():
    database = current_app.config["DATABASE_NAME"]
    if "db" not in g:  # g is Flask's context for request
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row  # rows behave like dictionaries
    return g.db


def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@home.route("/", methods=["GET", "POST"])
def home_f():
    route = request.form.get("route")
    url = request.form.get("url")
    action = request.form.get("action")

    if action == "generate":
        # set limit for generate method
        count = session.get("count", 0)
        if count < current_app.config.get("ROUTE_GENERATE_LIMIT", 10):
            count += 1
            session["count"] = count
            return render_template("index.html", route=generate_route())
        else:
            return render_template("index.html", error="you reached the limit.")

    if action == "submit":
        if route and url:
            if forbiden_words(route):
                return render_template(
                    "index.html",
                    result=f"Cannot register route using “{route}” because “{route}” is already reserved by an existing route in this application; choose a different parameter name.",
                )
            else:
                # checking if url is valid
                if not is_valid_url(url):
                    return render_template("index.html", error="URL is not valid")

                if not route.isalnum():
                    return render_template("index.html", error="Route is not valid")

                # checking if the route is already exist or not. every route should be unique.
                result = (
                    Redirect.query.with_entities(Redirect.route)
                    .filter_by(route=route)
                    .first()
                )
                print(result)
                if result == None:
                    id = session.get("id")
                    new_redirect = Redirect(route=route, url=url, created_by=id)
                    db.session.add(new_redirect)
                    db.session.commit()
                    # resetting to generate method for the next submition
                    session["count"] = 0
                    return render_template("index.html", result="operation successful")
                else:
                    return render_template(
                        "index.html", error="operation failed, route already exists"
                    )
        else:
            return render_template("index.html", error="fill up all the feilds")
    return render_template("index.html")
