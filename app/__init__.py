from flask import Flask, jsonify

from .extensions import db
from .cli import register_cli


def create_app(config_object: str | None = None) -> Flask:
    app = Flask(__name__)

    if config_object:
        app.config.from_object(config_object)
    else:
        # Default runtime config
        from config import Config

        app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    register_cli(app)

    # Register blueprints
    with app.app_context():
        from .routes.auth import auth_bp
        from .routes.users import users_bp

        app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
        app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    # Health check
    @app.get("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    # Error handlers for consistent JSON responses
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "bad_request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "unauthorized", "message": str(error)}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "not_found", "message": "resource not found"}), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({"error": "conflict", "message": str(error)}), 409

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({"error": "unprocessable_entity", "message": str(error)}), 422

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "internal_server_error", "message": "something went wrong"}), 500

    return app
