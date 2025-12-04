-- Schema for Auth Service (MariaDB)

CREATE TABLE apps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) UNIQUE NOT NULL,
    description TEXT,
    active TINYINT(1) DEFAULT 1
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE,
    password VARCHAR(200) NOT NULL,
    active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    name VARCHAR(80) NOT NULL,
    description TEXT,
    UNIQUE(app_id, name),
    FOREIGN KEY (app_id) REFERENCES apps(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    UNIQUE(app_id, name),
    FOREIGN KEY (app_id) REFERENCES apps(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE user_roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    app_id INT NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id, app_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (app_id) REFERENCES apps(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE token_blocklist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jti VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
