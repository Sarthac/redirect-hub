from flask import Blueprint, redirect, render_template, abort
from helper.utils import forbiden_words
from models.table import Redirect


redirect_bp = Blueprint("redirect_bp", __name__)


@redirect_bp.route("/<string:route>", methods=["GET"])
def url_redirect(route):
    if forbiden_words(route):
        return render_template(f"{route}.html")
    else:
        result = (
            Redirect.query.with_entities(Redirect.url).filter_by(route=route).scalar()
        )
        if result is None:
            return render_template(
                "error.html", error="Route does not exists.", code=404
            )
        return redirect(result)
