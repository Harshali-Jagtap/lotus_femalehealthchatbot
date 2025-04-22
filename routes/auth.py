# ===== Imports =====
from flask import Blueprint, flash, request, render_template, session, jsonify, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError
import bcrypt
import jwt
import os
from bson import ObjectId  # Import ObjectId
from security.db import db_instance  # Reusable DB connection

# ===== FLASK Config =====
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
auth_bp = Blueprint("auth", __name__, template_folder="templates")

# MongoDB Collection: Users
users_collection = db_instance.get_collection("users")

# Rate limiter for security (e.g., prevent brute-force)
limiter = Limiter(get_remote_address)


# ===== Helper Functions =====

# Check if a user account is temporarily locked
def is_account_locked(email):
    user = users_collection.find_one({"email": email})
    if user and "failed_attempts" in user:
        if user["failed_attempts"] >= 5 and user["lock_until"] > datetime.now(timezone.utc):  # Fix timezone issue
            return True
    return False


# Reset login attempts
def reset_failed_attempts(email):
    users_collection.update_one({"email": email}, {"$set": {"failed_attempts": 0, "lock_until": None}})


# Increase failed login attempts and possibly lock an account
def increase_failed_attempts(email):
    user = users_collection.find_one({"email": email})
    if user:
        failed_attempts = user.get("failed_attempts", 0) + 1
        lock_until = datetime.now(timezone.utc) + timedelta(
            minutes=15) if failed_attempts >= 5 else None  # Fix timezone issue
        users_collection.update_one({"email": email},
                                    {"$set": {"failed_attempts": failed_attempts, "lock_until": lock_until}})


# ===== Routes =====

# Route: Chatbot access (requires login)
@auth_bp.route("/chatbot")
def chatbot():
    """Render chatbot page only if a user is logged in."""
    if "user_id" not in session:
        return render_template("login.html")

    user = users_collection.find_one({"_id": ObjectId(session["user_id"])})  # Convert session ID to ObjectId

    if not user:
        return render_template("login.html")

    print("SESSION AT CHATBOT:", session)  # Debugging print
    return render_template("chatbot.html", user=user)


# Route: Register a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    """Handles user registration."""
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

    firstname = data.get("firstname")
    lastname = data.get("lastname")
    age = data.get("age")
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        flash("Email already exists. Try logging in.", "danger")  # Show an error message
        return redirect("login.html")

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    users_collection.insert_one({
        "firstname": firstname,
        "lastname": lastname,
        "age": age,
        "email": email,
        "password": hashed_password,
        "failed_attempts": 0,
        "lock_until": None,
        "created_at": datetime.utcnow()
    })

    flash("Registration successful! Please login.", "success")  # Flash success message
    return redirect("login.html")


# Route: Login with email and password
@auth_bp.route("/login", methods=["POST"])
def login():
    """Handles user login and stores session."""
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        flash("Invalid email or password", "danger")
        return render_template("login.html")

    session["user_id"] = str(user["_id"])  # Store user ID in session
    session["email"] = user["email"]

    flash("Login successful!", "success")

    return redirect(url_for("auth.chatbot"))


# Route: Logout and return to home pag
@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear session data
    return render_template("index.html")


# Route: Forgot Password (generates JWT reset token)
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json
    email = data.get("email")

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "If this email exists, a reset link has been sent.", "status": "success"}), 200

    reset_token = jwt.encode(
        {"email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},  # Fix timezone issue
        SECRET_KEY,
        algorithm="HS256"
    )

    # TODO: Send `reset_token` via email to user
    return jsonify({"message": "A password reset link has been sent to your email.", "status": "success",
                    "token": reset_token}), 200  # Fix unused variable warning


# Route: Reset Password using JWT token
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    token = data.get("token")
    new_password = data.get("password")

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = decoded_token.get("email")
    except ExpiredSignatureError:
        return jsonify({"message": "Reset link expired.", "status": "error"}), 400
    except InvalidTokenError:
        return jsonify({"message": "Invalid reset link.", "status": "error"}), 400

    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})

    return render_template("login.html", success="Password reset successful. Please login.")
