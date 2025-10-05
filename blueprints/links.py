from flask import Blueprint, redirect, current_app, render_template

links = Blueprint("links", __name__)


@links.route("/tor", methods=["GET"])
def tor():
    tor_network = current_app.config.get("TOR_NETWORK", None)
    if tor_network:
        return redirect(tor_network)
    else:
        return render_template(
            "error.html", code=404, error="No tor network address found."
        )


@links.route("/i2p", methods=["GET"])
def i2p():
    i2p_network = current_app.config.get("I2P_NETWORK", None)
    if i2p_network:
        return redirect(i2p_network)
    else:
        return render_template(
            "error.html", code=404, error="No i2p network address found."
        )
