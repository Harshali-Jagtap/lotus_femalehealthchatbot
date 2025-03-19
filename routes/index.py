from flask import Blueprint, render_template

# Define the Blueprint
index_bp = Blueprint("index", __name__)

# Corrected Home Route (root `/`)
@index_bp.route("/")
def home():
    return render_template("index.html")

# About Route
@index_bp.route("/about")
def about():
    return render_template("about.html")

# Login Route
@index_bp.route("/login")
def login():
    return render_template("login.html")

# Register Route
@index_bp.route("/register")
def register():
    return render_template("register.html")

# Dashboard Route
@index_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")
