from flask import Flask
from dotenv import load_dotenv
import os
from flask_session import Session
from config import DevelopmentConfig, ProductionConfig
from extensions import db

# for cloudflare tunnel setup, My ISP does not allow port forwarding.
# from werkzeug.middleware.proxy_fix import ProxyFix

from blueprints.redirect_bp import redirect_bp
from blueprints.home import home
from blueprints.user import user
from blueprints.api import api
from blueprints.routes import route_bp

app = Flask(__name__)

# for cloudflare tunnel setup.
# app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

load_dotenv()

env = os.environ.get("FLASK_ENV")

if env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)

Session(app)
db.init_app(app)

app.register_blueprint(redirect_bp)
app.register_blueprint(home)
app.register_blueprint(user)
app.register_blueprint(api)
app.register_blueprint(route_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=app.config.get("HOST", "127.0.0.1"), port=app.config.get("PORT", 5000))
