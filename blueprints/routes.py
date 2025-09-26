from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    current_app,
    g,
)

from helper.utils import is_valid_url, validate_session

from extensions import db
from models.table import User, Redirect
from datetime import datetime


route_bp = Blueprint("route_bp", __name__)


@route_bp.route("/routes", methods=["GET", "POST"])
def routes():
    error = None
    if not validate_session():
        return redirect(url_for("user.login"))

    # if request.method == "GET":
    page = request.args.get("page", 1, type=int)

    if request.cookies.get("limit"):
        limit = int(request.cookies["limit"])
    else:
        limit = request.args.get(
            "limit", current_app.config.get("ROUTE_PAGE_LIMIT", 20), type=int
        )

    results = (
        Redirect.query.filter_by(created_by=session["id"])
        .order_by(Redirect.created_at.desc())
        .paginate(page=page, per_page=limit, max_per_page=50, error_out=False)
    )

    return render_template(
        "routes.html",
        session=session.get("session_id"),
        results=results,
        limit=limit,
        error=error,
    )


@route_bp.route("/routes/<string:route>", methods=["POST", "GET"])
def unique_route(route):
    # Check login
    if "id" not in session:
        error = "You need to login."
        code = 401
        return render_template("error.html", error=error, code=code)

    # Check ownership
    created_by = Redirect.find_using_route_and_created_by(
        route=route, created_by=session["id"]
    )
    if not created_by:
        error = "Route does not exist or you don't own this route."
        code = 404
        return render_template("error.html", error=error, code=code)

    unique_route = Redirect.query.filter_by(route=route).first()

    if request.method == "POST":
        if request.form.get("action") == "save":
            new_route = request.form.get("route")
            new_url = request.form.get("url")

            # Validate new route uniqueness
            if new_route and Redirect.route_exists(new_route):
                error = "New route already exists"
                return render_template(
                    "route_operations.html", route=unique_route, error=error
                )

            # Update fields based on what was submitted
            if new_route:
                unique_route.route = new_route
            if new_url:
                unique_route.url = new_url

            unique_route.updated_at = datetime.now()
            db.session.commit()

            # Redirect safely (fallback to current route if no new_route)
            return redirect(url_for("route_bp.unique_route", route=unique_route.route))
        if request.form.get("action") == "delete":
            db.session.delete(unique_route)
            db.session.commit()
            return redirect(url_for("route_bp.routes"))

    return render_template("route_operations.html", route=unique_route)
