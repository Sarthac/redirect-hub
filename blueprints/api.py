from flask import Blueprint, request, jsonify, g, render_template, current_app
from models.table import Redirect, Api
from extensions import db
from datetime import datetime
from helper.utils import generate_route, is_valid_url, is_valid_route
import markdown

api = Blueprint("api", __name__, url_prefix="/api")

from models.table import Api


@api.before_request
def check_api_key():
    # Allow public routes (like /api/test) to skip auth
    public_routes = ["/api/test", "/api"]
    if request.path in public_routes:
        return None

    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return jsonify({"error": "Missing API key"}), 400

    created_by = Api.get_api_id(api_key)
    if not created_by:
        return jsonify({"error": "Invalid API key"}), 403

    # Store user info in Flask's "g" (global context for request)
    g.created_by = created_by


@api.route("", methods=["GET"])
def api_doc():
    with open("docs/API.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
    html_content = markdown.markdown(markdown_content)
    return render_template("api_doc.html", html_content=html_content)


@api.route("/test", methods=["GET"])
def test():
    return jsonify({"data": "Server is operational."}), 200


@api.route("/routes", methods=["POST", "GET"])
def routes():

    if request.method == "GET":
        data = request.args
        limit = data.get("limit", 20, type=int)
        page = data.get("page", 1, type=int)
        sortBy = data.get("sortBy", "created_at")
        sortOrder = data.get("sortOrder", "asc")

        sort_by = {
            "created_at": Redirect.created_at,
            "route": Redirect.route,
            "url": Redirect.url,
            "updated_at": Redirect.updated_at,
        }

        column = sort_by.get(sortBy, Redirect.created_at)

        if sortOrder == "desc":
            order = column.desc()
        else:
            order = column.asc()

        pagination = (
            Redirect.query.filter_by(created_by=g.created_by)
            .order_by(order)
            .paginate(page=page, per_page=limit, max_per_page=20, error_out=False)
        )

        data = [
            {
                "route": item.route,
                "url": item.url,
                "created_at": str(item.created_at),
                "update_at": str(item.updated_at),
            }
            for item in pagination.items
        ]
        return (
            jsonify(
                {
                    "data": data,
                    "total": pagination.total,
                    "page": pagination.page,
                    "totalPages": pagination.pages,
                }
            ),
            200,
        )

    if request.method == "POST":
        data = request.get_json()
        if data:

            url = data.get("url")
            route = data.get("route")

            if not url:
                return (jsonify({"error": "'url' are required"}), 400)

            if url and not is_valid_url(url):
                return jsonify({"error": "url is not valid."}), 400

            if route:
                if not is_valid_route(route):
                    return (
                        jsonify(
                            {
                                "error": "route is not valid, route only contain letters, digits, '-' and '_' "
                            }
                        ),
                        400,
                    )

                if route in current_app.config["FORBIDEN_ROUTES"]:
                    return (
                        jsonify(
                            {
                                "error": f"Cannot register route using “{route}” because “{route}” is already reserved by an existing route in this application; choose a different route."
                            }
                        ),
                        400,
                    )

                if Redirect.route_exists(route):
                    return (
                        jsonify(
                            {"error": "Route already exists, provide unique route"}
                        ),
                        400,
                    )
            if not route:
                # generating unique route if the client does not provide the route
                route: str = generate_route()
                while Redirect.route_exists(route):
                    route: str = generate_route()

            new_route = Redirect(route=route, url=url, created_by=g.created_by)
            db.session.add(new_route)
            db.session.commit()
            return jsonify({"data": {"route": route, "url": url}}), 201

    return jsonify({"error": "Only 'GET' and 'POST' allowed"}), 405


@api.route("/routes/<string:route>", methods=["PATCH", "DELETE", "GET"])
def update(route):
    # checking if route exists
    route_exists = Redirect.route_exists(route)
    if not route_exists:
        return jsonify({"error": "Route does not exist."}), 404

    # reusing and checkig proper parameters and conditions in both delete and get request
    if request.method == "DELETE" or request.method == "GET":
        entry = Redirect.query.filter_by(route=route, created_by=g.created_by).first()

        if not entry:
            return jsonify({"error": "You don't own this route."}), 403

        # GET request
        if request.method == "GET":
            return (
                jsonify(
                    {
                        "data": {
                            "route": entry.route,
                            "url": entry.url,
                            "created_at": str(entry.created_at),
                            "update_at": str(entry.updated_at),
                        }
                    }
                ),
                200,
            )

        # DELETE request
        db.session.delete(entry)
        db.session.commit()
        return "", 204

    # PATCH route
    if request.method == "PATCH":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body required"}), 400

        entry = Redirect.query.filter_by(route=route, created_by=g.created_by).first()
        if not entry:
            return jsonify({"error": "You don't own this route."}), 403

        new_url = data.get("url")
        new_route = data.get("route")

        # clinet should provide at least one parameter.
        if not new_url and not new_route:
            return jsonify({"error": "Must provide 'url' or 'route' to update."}), 400

        # validating if the new route is already exists or not.
        if new_route and Redirect.route_exists(new_route):
            return jsonify({"error": "New route already exists"}), 400

        # if two params provide update both of them
        if new_route and new_url:
            entry.route = new_route
            entry.url = new_url

        # else update each on of them
        elif new_url:
            entry.url = new_url
        elif new_route:
            entry.route = new_route

        entry.updated_at = datetime.now()
        db.session.commit()
        return jsonify({"message": "Route updated successfully."}), 200

    return jsonify({"error": "Only 'PATCH' or 'DELETE' supported."})
