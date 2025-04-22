# ===== Flask Blueprint: Index Page =====
from flask import Blueprint, render_template

# ========== BLUEPRINT ==========
index_bp = Blueprint("index", __name__)


# ===== Home Page =====
@index_bp.route("/")
def home():
    return render_template("index.html")


# ===== Dashboard Page =====
@index_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ===== Login Page =====
@index_bp.route("/login")
def login():
    return render_template("login.html")


# ===== Register Page =====
@index_bp.route("/register")
def register():
    return render_template("register.html")


# ===== Mental Health Page =====
@index_bp.route("/mental_health")
def mental_health():
    return render_template("mental_health.html")


# ===== Female Health Page =====
@index_bp.route("/female_health")
def female_health():
    return render_template("female_health.html")


# ===== About Page =====
@index_bp.route("/about")
def about():
    return render_template("about.html")


# ===== Footer Partial Page =====
@index_bp.route("/footer")
def footer_partial():
    return render_template("footer.html")
