from datetime import datetime
from extensions import db

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True)
)

class App(db.Model):
    __tablename__ = "apps"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)

    roles = db.relationship("Role", backref="app", lazy="dynamic")
    permissions = db.relationship("Permission", backref="app", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "active": self.active}

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email, "active": self.active}

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255))

    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles", lazy="dynamic")
    user_roles = db.relationship("UserRole", back_populates="role", lazy="dynamic")

    __table_args__ = (db.UniqueConstraint('app_id', 'name', name='uq_role_app_name'),)

    def to_dict(self):
        return {"id": self.id, "app_id": self.app_id, "name": self.name, "description": self.description}

class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))

    __table_args__ = (db.UniqueConstraint('app_id', 'name', name='uq_perm_app_name'),)

    def to_dict(self):
        return {"id": self.id, "app_id": self.app_id, "name": self.name, "description": self.description}

class UserRole(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False, index=True)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("user_roles", lazy="dynamic"))
    role = db.relationship("Role", back_populates="user_roles")

    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', 'app_id', name='uq_user_role_app'),)

class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(200), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
