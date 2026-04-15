import logging
import sys
from flask import Flask
from flask_cors import CORS
from config import config, SCRIPT_DIR
from routes import bp as main_bp


def create_app():
    app = Flask(__name__, template_folder=str(SCRIPT_DIR / "templates"), static_folder=str(SCRIPT_DIR / "static"))

    app.config["SECRET_KEY"] = config.secret_key
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length_mb * 1024 * 1024

    CORS(app)

    # Logger
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, encoding="utf-8")
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    # Register routes
    app.register_blueprint(main_bp)

    return app


app = create_app()

if __name__ == "__main__":
    print(f"Lancement de UnityAssetsManager sur {config.flask_host}:{config.flask_port}")
    app.run(host=config.flask_host, port=config.flask_port, debug=config.flask_debug, threaded=config.flask_threaded)
