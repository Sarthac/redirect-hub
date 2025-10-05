from flask import Blueprint, redirect, render_template, current_app
from models.table import Redirect


redirect_bp = Blueprint("redirect_bp", __name__)


@redirect_bp.route("/<string:route>", methods=["GET"])
def url_redirect(route):
    result = Redirect.query.with_entities(Redirect.url).filter_by(route=route).scalar()
    if result is None:
        if route in current_app.config["LINKS"]:
            return redirect(current_app.config["LINKS"][route], code=301)
        return render_template("error.html", error="Route does not exists.", code=404)
    return redirect(result)
