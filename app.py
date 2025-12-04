from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from extensions import db, migrate, jwt
from routes_auth import bp as auth_bp
from routes_admin import bp as admin_bp
from models import TokenBlocklist

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    @app.route("/health")
    def health():
        return jsonify({"status":"ok"}), 200

    # JWT callbacks
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"msg":"missing token", "reason": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"msg":"invalid token", "reason": reason}), 401

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
