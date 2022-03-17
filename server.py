import os
from flask import Flask
from flask import url_for
from database import mongo


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"
    app.config[
        "MONGO_URI"
    ] = "mongodb+srv://[MONGO_URI]"
    mongo.init_app(app)

    def override_url_for():
        return dict(url_for=dated_url_for)

    def dated_url_for(endpoint, **values):
        if endpoint == "static":
            filename = values.get("filename", None)
            if filename:
                file_path = os.path.join(app.root_path, endpoint, filename)
                values["q"] = int(os.stat(file_path).st_mtime)
        return url_for(endpoint, **values)

    from main.main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from auth.auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from api.api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    app.run(port=5000, debug=True)


if __name__ == "__main__":
    create_app()
