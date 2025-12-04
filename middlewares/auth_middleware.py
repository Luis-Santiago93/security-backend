import requests
from functools import wraps
from flask import request, jsonify

AUTH_MICROSERVICE_URL = "http://localhost:5000/api/auth/verify-token"   # <-- cámbialo

def require_auth(permission=None):

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):

            # ----------------------------------------------------
            # 1️⃣ Obtener Bearer Token desde los headers
            # ----------------------------------------------------
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Authorization header required"}), 401
            
            if not token.startswith("Bearer "):
                return jsonify({"error": "Invalid Authorization format"}), 401

            token = token.replace("Bearer ", "")

            # ----------------------------------------------------
            # 2️⃣ Obtener el APP_ID de esta aplicación
            # ----------------------------------------------------
            app_id = request.headers.get("X-App-ID")
            if not app_id:
                return jsonify({"error": "X-App-ID header required"}), 400

            try:
                app_id = int(app_id)
            except:
                return jsonify({"error": "X-App-ID must be numeric"}), 400

            # ----------------------------------------------------
            # 3️⃣ Validar contra auth-microservice (MODELO A)
            # ----------------------------------------------------
            try:
                response = requests.post(AUTH_MICROSERVICE_URL, json={"token": token})
                data = response.json()
            except Exception as e:
                print("AUTH SERVER ERROR:", e)
                return jsonify({"error": "Auth Server unreachable"}), 503

            if response.status_code != 200 or not data.get("valid"):
                return jsonify({"error": "Invalid or revoked token"}), 401

            # ----------------------------------------------------
            # 4️⃣ Extraer información del usuario validado
            # ----------------------------------------------------
            claims = data.get("claims", {})
            apps = claims.get("apps", [])

            # ----------------------------------------------------
            # 5️⃣ Validar que el usuario tenga acceso a ESTA app
            # ----------------------------------------------------
            user_app = next((a for a in apps if a["app_id"] == app_id), None)

            if not user_app:
                return jsonify({"error": "User not authorized for this application"}), 403

            # ----------------------------------------------------
            # 6️⃣ Validar permisos (si el endpoint los requiere)
            # ----------------------------------------------------
            if permission:
                if permission not in user_app.get("permissions", []):
                    return jsonify({"error": "Permission denied"}), 403

            # ----------------------------------------------------
            # 7️⃣ Guardar datos del usuario para los endpoints
            # ----------------------------------------------------
            request.user_id = data.get("user_id")
            request.apps = apps
            request.current_app_id = app_id
            request.current_roles = user_app.get("roles", [])
            request.current_permissions = user_app.get("permissions", [])

            return f(*args, **kwargs)
        return wrapper
    
    return decorator
