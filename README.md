# 🛡️ Dot7 - Security Service (Flask)  
Backend de Autenticación, Roles y Permisos

Este proyecto es el **microservicio de seguridad** del ecosistema **Dot7**, encargado de gestionar:

🔐 Autenticación  
👥 Usuarios  
🧩 Roles  
🛂 Permisos  
🏛️ Múltiples aplicaciones (multi-app)  
🔑 Access & Refresh Tokens con protección avanzada  

---

## 🚀 Tecnologías Utilizadas

- **Python 3**
- **Flask**
- **SQLAlchemy**
- **Flask-Migrate** (migraciones)
- **JWT (access / refresh tokens)**
- **Blocklist de tokens (logout seguro)**

---

## ⚙️ Instalación y uso local

### 1. 🔁 Clona el repositorio

```bash
git clone https://github.com/Luis-Santiago93/security-service.git
cd security-service
```

### 2. 🐍 Crea y activa el entorno virtual

#### Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 📥 Instala dependencias

```bash
pip install -r requirements.txt
```

### 4. ⚙️ Configura variables de entorno

Copia el archivo:

```bash
cp .env.example .env
```

Edita los valores según tu entorno (database, JWT secret, expiraciones, etc.).

---

## 🗄️ Migraciones (Base de datos)

Si usas **Flask-Migrate**, ejecuta:

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "initial"
flask db upgrade
```

---

## ▶️ Ejecutar en modo desarrollo

```bash
python app.py
```

---

## 🔐 Endpoints principales

### Autenticación
- **POST** `/api/auth/register`
- **POST** `/api/auth/login`
- **POST** `/api/auth/refresh`
- **POST** `/api/auth/logout`

### Administración de Apps, Roles, Permisos
- **POST** `/api/admin/apps`
- **POST** `/api/admin/apps/<id>/roles`
- **POST** `/api/admin/apps/<id>/permissions`
- **POST** `/api/admin/roles/<role_id>/permissions`
- **POST** `/api/admin/users/<user_id>/roles`

---

## 🛡️ Seguridad con Decoradores

El microservicio incluye el decorador:

```python
@require_permission(app_id, permission_name)
```

Esto permite proteger cualquier endpoint verificando que el usuario tenga los permisos correspondientes.

---

## 👥 Desarrollado por el equipo de Dot7

Microservicio oficial del ecosistema **Dot7 Security** 🔐✨
