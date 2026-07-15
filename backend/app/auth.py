"""Authentication helpers for registration, login, and session protection."""

from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from app.analytics import log_event
from functools import wraps
from flask import session, jsonify


def register_user(name, email, password):
    """Register a new user and record a registration event."""
    conn = get_db()
    cursor = conn.cursor()

    password_hash = generate_password_hash(password)

    try:
        # Use parameterized SQL placeholders to safely insert user-provided values.
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (?, ?, ?)
        """, (name, email, password_hash))

        # Retrieve the ID automatically generated for the new user.
        user_id = cursor.lastrowid
        conn.commit()

        # Record the successful registration for analytics and activity tracking.
        log_event(user_id, "register", {"email": email})

        return {
            "success": True,
            "user_id": user_id,
            "message": "User registered successfully"
        }

    except Exception as error:
        return {
            "success": False,
            "message": str(error)
        }

    finally:
        conn.close()


def login_user(email, password):
    """Authenticate a user by email and password."""
    conn = get_db()

    try:
        cursor = conn.cursor()

        # Look up the user by email using a parameterized query.
        cursor.execute("""
                SELECT *
                FROM users
                WHERE email = ?
            """, (email,))

        user = cursor.fetchone()

    finally:
        conn.close()

    if user is None:
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    if not check_password_hash(user["password_hash"], password):
        return {
            "success": False,
            "message": "Invalid email or password"
        }

    log_event(user["id"], "login", {"email": email})

    # if login succeeded, return user information dictionary
    return {
        "success": True,
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "message": "Login successful"
    }


def login_required(f):
    """Require a logged-in user before serving the route."""
    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper