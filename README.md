# Summary
A Flask app was scaffolded, including SQLAlchemy setup.

A User model in app/models/user.py was created, featuring:
Password hashing via set_password.
Email validation in normalize_email.
JWT token generation/verification with generate_token/verify_token.

REST endpoints for user registration (/api/v1/auth/register) and login (/api/v1/auth/login) were added in app/routes/auth.py.
User management endpoints (/api/v1/users) with JWT authentication were implemented in app/routes/users.py.
A flask init-db CLI command was also added for database initialization.
