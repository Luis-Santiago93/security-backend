from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import App, Role, Permission, User, UserRole

def require_permission(app_id, permission_name):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # ensure JWT present
            try:
                verify_jwt_in_request()
            except Exception as e:
                return jsonify({"msg":"missing or invalid token", "error": str(e)}), 401

            claims = get_jwt()
            identity = get_jwt_identity()

            # First try: check claims included in token (apps claim)
            apps_claim = claims.get("apps", [])
            for a in apps_claim:
                if a.get("app_id") == int(app_id):
                    if permission_name in a.get("permissions", []):
                        return fn(*args, **kwargs)
                    break

            # Fallback: check DB (in case roles changed)
            user_roles = UserRole.query.filter_by(user_id=identity, app_id=app_id).all()
            perms = set()
            for ur in user_roles:
                role = ur.role
                for p in role.permissions:
                    perms.add(p.name)
            if permission_name in perms:
                return fn(*args, **kwargs)

            return jsonify({"msg":"forbidden"}), 403
        return wrapper
    return decorator
