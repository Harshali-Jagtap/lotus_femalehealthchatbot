# ===== Imports =====
from flask import Blueprint, flash, request, render_template, session, jsonify, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta, timezone
from jwt import ExpiredSignatureError, InvalidTokenError
import bcrypt, jwt, os, re
from bson import ObjectId  # Import ObjectId
from security.db import db_instance  # Reusable DB connection
from flask import current_app
from flask_mail import Mail, Message

# ===== FLASK Config =====
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
auth_bp = Blueprint("auth", __name__, template_folder="templates")

# Mail configuration (you can change this to any working real SMTP)
mail = Mail()

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
    """Handles user registration with password strength validation."""
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

    firstname = data.get("firstname")
    lastname = data.get("lastname")
    age = data.get("age")
    email = data.get("email")
    password = data.get("password")

    # Check if email already exists
    if users_collection.find_one({"email": email}):
        flash("Email already exists. Try logging in.", "danger")
        return redirect(url_for("auth.render_login_form"))

    # Password strength rule enforcement
    import re
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_pattern, password):
        flash(
            "Password must be at least 8 characters long, contain upper and lower case letters, a number, and a special character.",
            "danger")
        return redirect(url_for("auth.render_login_form"))

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Save user
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

    flash("Registration successful! Please login.", "success")
    return redirect(url_for("auth.render_login_form"))


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


@auth_bp.route("/login", methods=["GET"])
def render_login_form():
    return render_template("login.html")


# Route: Logout and return to home pag
@auth_bp.route("/logout", methods=["GET"])
def logout():
    session.clear()  # Clear session data
    return render_template("index.html")


# Route: Forgot Password (generates JWT reset token)
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    # Support both form (HTML) and JSON (API) submissions
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

    email = data.get("email")

    user = users_collection.find_one({"email": email})
    if not user:
        # Always respond generically to avoid email enumeration
        if request.content_type == "application/json":
            return jsonify({"message": "If this email exists, a reset link has been sent.", "status": "success"}), 200
        flash("If this email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.render_forgot_password_form"))

    # Generate JWT reset token
    reset_token = jwt.encode(
        {"email": email, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        SECRET_KEY,
        algorithm="HS256"
    )

    reset_link = f"http://localhost:5000/reset-password?token={reset_token}"

    # Send reset email
    msg = Message("Lotus - Password Reset",
                  sender=current_app.config["MAIL_USERNAME"],
                  recipients=[email])
    msg.body = f"""
    Hello,

    You requested a password reset for your Lotus account.
    Click the link below to reset your password (valid for 15 minutes):

    {reset_link}

    If you didn't request this, please ignore this email.

    Regards,
    Lotus Team
    """

    mail.send(msg)

    if request.content_type == "application/json":
        return jsonify({
            "message": "A password reset link has been sent to your email.",
            "status": "success",
            "token": reset_token
        }), 200
    else:
        flash("A password reset link has been sent to your email.", "success")
        return redirect(url_for("auth.render_forgot_password_form"))


@auth_bp.route("/forgot-password", methods=["GET"])
def render_forgot_password_form():
    return render_template("forgot_password.html")


# Route: Reset Password using JWT token and Mail Trap
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    if request.content_type == "application/json":
        data = request.get_json()
    else:
        data = request.form

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


@auth_bp.route("/reset-password", methods=["GET"])
def render_reset_form():
    token = request.args.get("token")
    return render_template("reset_password.html", token=token)
