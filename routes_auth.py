from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, jwt
from models import User, App, Role, Permission, UserRole, TokenBlocklist
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, decode_token
import jwt

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# register
@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"msg": "user already exists"}), 409

    user = User(username=username, email=email, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "user created", "user": user.to_dict()}), 201

# login: produce access + refresh with aggregated apps/roles/permissions
@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "username and password required"}), 400

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "invalid credentials"}), 401

    # build apps structure: for each app where user has roles, include roles and derived permissions
    apps = []
    # group user's roles by app
    for ur in user.user_roles:
        app = App.query.get(ur.app_id)
        if not app:
            continue
        role = ur.role
        # find permissions for the role
        perms = [p.name for p in role.permissions]
        # try to find existing app entry
        entry = next((a for a in apps if a["app_id"] == app.id), None)
        if entry:
            if role.name not in entry["roles"]:
                entry["roles"].append(role.name)
            for p in perms:
                if p not in entry["permissions"]:
                    entry["permissions"].append(p)
        else:
            apps.append({
                "app_id": app.id,
                "app_name": app.name,
                "roles": [role.name],
                "permissions": perms
            })

    additional_claims = {"apps": apps}
    access = create_access_token(identity=user.id, additional_claims=additional_claims)
    refresh = create_refresh_token(identity=user.id)
    return jsonify({"access_token": access, "refresh_token": refresh, "user": user.to_dict(), "apps": apps}), 200

# refresh
@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({"msg": "user not found"}), 404

    # Rebuild apps on refresh to include updated roles/permissions
    apps = []
    for ur in user.user_roles:
        app = App.query.get(ur.app_id)
        if not app:
            continue
        role = ur.role
        perms = [p.name for p in role.permissions]
        entry = next((a for a in apps if a["app_id"] == app.id), None)
        if entry:
            if role.name not in entry["roles"]:
                entry["roles"].append(role.name)
            for p in perms:
                if p not in entry["permissions"]:
                    entry["permissions"].append(p)
        else:
            apps.append({
                "app_id": app.id,
                "app_name": app.name,
                "roles": [role.name],
                "permissions": perms
            })

    additional_claims = {"apps": apps}
    new_access = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify({"access_token": new_access}), 200

# logout (revoke access)
@bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    tb = TokenBlocklist(jti=jti)
    db.session.add(tb)
    db.session.commit()
    return jsonify({"msg":"access token revoked"}), 200

# logout refresh
@bp.route("/logout-refresh", methods=["DELETE"])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()["jti"]
    tb = TokenBlocklist(jti=jti)
    db.session.add(tb)
    db.session.commit()
    return jsonify({"msg":"refresh token revoked"}), 200

# protected example
@bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    claims = get_jwt()
    identity = get_jwt_identity()
    return jsonify({"msg":"hi", "user_id": identity, "claims": claims}), 200

@bp.route("/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json() or {}
    token = data.get("token")

    if not token:
        return jsonify({"error": "token required"}), 400
    try:
        # intenta decodificar el token
        decoded = decode_token(token)

        # verificar si el token está en blocklist
        jti = decoded.get("jti")
        if TokenBlocklist.query.filter_by(jti=jti).first():
            return jsonify({"error": "token revoked"}), 401

        # obtener el usuario
        user_id = decoded.get("sub")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "user not found"}), 404

        # extraer claims (roles, apps, permisos)
        claims = decoded.get("claims", decoded)

        return jsonify({
            "valid": True,
            "user_id": user_id,
            "claims": claims
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "token expired"}), 401

    except Exception as e:
        print("VERIFY ERROR:", e)
        return jsonify({"error": "invalid token"}), 401