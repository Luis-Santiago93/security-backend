-- ------------------------------------------------------
-- INSERTS PARA apps
-- ------------------------------------------------------
INSERT INTO apps (name, description, active)
VALUES 
('auth', 'Internal authentication and authorization service', 1),
('dashboard', 'Main web dashboard application', 1);

-- ------------------------------------------------------
-- INSERTS PARA users
-- (password = admin123 en bcrypt)
-- ------------------------------------------------------
INSERT INTO users (username, email, password, active)
VALUES 
('admin', 'admin@example.com', 
'$2y$10$gLmDZp1Zx1xRP9DpGS6yCOWYfTo75BDuS3sWznuaCG2lLBVmOAXLC', 
1);

-- ------------------------------------------------------
-- INSERTS PARA roles
-- ------------------------------------------------------
INSERT INTO roles (app_id, name, description)
VALUES
(1, 'superadmin', 'Full access to all features'),
(1, 'admin', 'Administrative access'),
(2, 'viewer', 'Read-only dashboard user');

-- ------------------------------------------------------
-- INSERTS PARA permissions
-- ------------------------------------------------------
INSERT INTO permissions (app_id, name, description)
VALUES
(1, 'manage_users', 'Create, edit and delete users'),
(1, 'manage_roles', 'Create, edit and delete roles'),
(1, 'manage_permissions', 'Control permissions'),
(2, 'view_dashboard', 'View dashboard overview'),
(2, 'view_reports', 'See reports');

-- ------------------------------------------------------
-- INSERTS PARA role_permissions
-- Dar TODO al superadmin (role_id = 1)
-- ------------------------------------------------------
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, id FROM permissions;

-- ------------------------------------------------------
-- INSERTS PARA user_roles
-- Asignar superadmin al usuario admin
-- ------------------------------------------------------
INSERT INTO user_roles (user_id, role_id, app_id)
VALUES (1, 1, 1);
