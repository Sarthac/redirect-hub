from flask import Flask
from dotenv import load_dotenv
from helper.db import close_db
import os
from helper.db import init_db
from flask_session import Session
from config import DevelopmentConfig, ProductionConfig
from extensions import db


from blueprints.redirect_bp import redirect_bp
from blueprints.home import home
from blueprints.user import user
from blueprints.api import api

app = Flask(__name__)
load_dotenv()


env = os.environ.get("FLASK_ENV")


if env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(ProductionConfig)


Session(app)
db.init_app(app)
with app.app_context():
    db.create_all()


app.register_blueprint(redirect_bp)
app.register_blueprint(home)
app.register_blueprint(user)
app.register_blueprint(api)


@app.teardown_appcontext
def close_database(error):
    close_db(error)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host=app.config.get("HOST", "127.0.0.1"), port=app.config.get("PORT", 5000))
