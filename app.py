# ============================================================================
# UnityAssetsManager - app.py
# ============================================================================
# Description: Flask application entry point and initialization.
# Version: 1.2.16
# ============================================================================

import logging
from flask import Flask
from flask import request
from flask_cors import CORS
from lib.config import config, SCRIPT_DIR
from lib.routes import bp as main_bp
from lib.errors import AppError, ErrorCode, create_error_response
from lib.logging_setup import configure_logging
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, template_folder=str(SCRIPT_DIR / "templates"), static_folder=str(SCRIPT_DIR / "static"))

    app.config["SECRET_KEY"] = config.secret_key
    app.config["MAX_CONTENT_LENGTH"] = config.max_content_length_mb * 1024 * 1024

    CORS(app)

    # Logger
    configure_logging(
        log_level=config.log_level,
        log_output=config.log_output,
        log_max_bytes=config.log_max_bytes,
        log_backup_count=config.log_backup_count,
        log_file_path=SCRIPT_DIR / config.log_file,
    )

    # Register routes
    app.register_blueprint(main_bp)

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return create_error_response(code=error.code, message=error.message, http_status=error.http_status, details=error.details, )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        if isinstance(error, HTTPException):
            if request.path.startswith("/api/"):
                return create_error_response(
                    code=ErrorCode.HTTP_ERROR,
                    message=error.description or "Erreur HTTP",
                    http_status=error.code or 500,
                    details={"name": error.name},
                )
            return error

        logger.exception("Unhandled exception")
        if request.path.startswith("/api/"):
            return create_error_response(
                code=ErrorCode.INTERNAL_ERROR, message="Erreur interne du serveur", http_status=500, details={"exception": type(error).__name__},
            )
        return "Internal Server Error", 500

    return app


app = create_app()

if __name__ == "__main__":
    server_port = config.server_port
    server_host = config.server_host
    flask_debug = config.flask_debug
    flask_threaded = config.flask_threaded
    print("🚀 UnityAssetsManager")
    print("=" * 40)
    print(f"\nOpen: http://{server_host}:{server_port}\n")
    if flask_debug:
        print("✅ FLASK DEBUGGER ON")
    if flask_threaded:
        print("✅ FLASK THREADING ON")
    app.run(debug=flask_debug, host=server_host, port=server_port, threaded=flask_threaded)
