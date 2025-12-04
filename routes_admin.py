from flask import Blueprint, request, jsonify
from extensions import db
from models import App, Role, Permission, User, UserRole

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# Create an app
@bp.route("/apps", methods=["POST"])
def create_app():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"msg":"name required"}), 400
    if App.query.filter_by(name=name).first():
        return jsonify({"msg":"app already exists"}), 409
    app = App(name=name, description=description)
    db.session.add(app)
    db.session.commit()
    return jsonify({"msg":"app created", "app": app.to_dict()}), 201

# Create a role for an app
@bp.route("/apps/<int:app_id>/roles", methods=["POST"])
def create_role(app_id):
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"msg":"name required"}), 400
    if not App.query.get(app_id):
        return jsonify({"msg":"app not found"}), 404
    if Role.query.filter_by(app_id=app_id, name=name).first():
        return jsonify({"msg":"role exists"}), 409
    role = Role(app_id=app_id, name=name, description=description)
    db.session.add(role)
    db.session.commit()
    return jsonify({"msg":"role created", "role": role.to_dict()}), 201

# Create a permission for an app
@bp.route("/apps/<int:app_id>/permissions", methods=["POST"])
def create_permission(app_id):
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"msg":"name required"}), 400
    if not App.query.get(app_id):
        return jsonify({"msg":"app not found"}), 404
    if Permission.query.filter_by(app_id=app_id, name=name).first():
        return jsonify({"msg":"permission exists"}), 409
    perm = Permission(app_id=app_id, name=name, description=description)
    db.session.add(perm)
    db.session.commit()
    return jsonify({"msg":"permission created", "permission": perm.to_dict()}), 201

# assign permission to role
@bp.route("/roles/<int:role_id>/permissions", methods=["POST"])
def assign_permission_to_role(role_id):
    data = request.get_json() or {}
    perm_id = data.get("permission_id")
    role = Role.query.get(role_id)
    perm = Permission.query.get(perm_id)
    if not role or not perm:
        return jsonify({"msg":"role or permission not found"}), 404
    if perm in role.permissions:
        return jsonify({"msg":"already assigned"}), 409
    role.permissions.append(perm)
    db.session.commit()
    return jsonify({"msg":"permission assigned"}), 200

# assign role to user (for a specific app)
@bp.route("/users/<int:user_id>/roles", methods=["POST"])
def assign_role_to_user(user_id):
    data = request.get_json() or {}
    role_id = data.get("role_id")
    app_id = data.get("app_id")
    user = User.query.get(user_id)
    role = Role.query.get(role_id)
    if not user or not role:
        return jsonify({"msg":"user or role not found"}), 404
    if role.app_id != app_id:
        return jsonify({"msg":"role does not belong to the app provided"}), 400
    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id, app_id=app_id).first()
    if existing:
        return jsonify({"msg":"already assigned"}), 409
    ur = UserRole(user_id=user_id, role_id=role_id, app_id=app_id)
    db.session.add(ur)
    db.session.commit()
    return jsonify({"msg":"role assigned to user"}), 200
