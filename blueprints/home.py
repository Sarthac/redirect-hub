from flask import Blueprint, request, render_template, session, current_app
from helper.utils import is_valid_url, is_valid_route, generate_route
from extensions import db
from models.table import Redirect

home = Blueprint("home", __name__)


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
            if route in current_app.config["FORBIDEN_ROUTES"]:
                return render_template(
                    "index.html",
                    error=f"Cannot register route using “{route}” because “{route}” is already reserved by an existing route in this application; choose a different parameter name.",
                )
            else:
                # checking if url is valid
                if not is_valid_url(url):
                    return render_template("index.html", error="URL is not valid")

                if not is_valid_route(route):
                    return render_template(
                        "index.html",
                        error="Route is not valid, route only containing letters, digits, '-', '_' are valid",
                    )

                # checking if the route is already exist or not. every route should be unique.
                result = (
                    Redirect.query.with_entities(Redirect.route)
                    .filter_by(route=route)
                    .first()
                )
                if result == None:
                    if session:
                        id = session.get("id")
                    else:
                        id = None
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
