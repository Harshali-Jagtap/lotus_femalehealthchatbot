# ===== SYSTEM IMPORTS =====
import os, logging, warnings
from dotenv import load_dotenv

# ===== Load environment variables from .env =====
load_dotenv()

# ===== FLASK CORE =====
from flask import Flask, render_template, session, redirect, url_for, request

# ===== BLUEPRINT IMPORTS =====
from routes.auth import auth_bp
from routes.chatbot import chatbot_bp
from routes.dashboard import dashboard_bp
from routes.index import index_bp
from routes.about import about_bp
from routes.mental_health import mental_health_bp
from routes.female_health import female_health_bp
from routes.gdpr import gdpr_bp


# ===== TRANSFORMER WARNING CONFIG =====
from transformers import logging as transformers_logging

warnings.filterwarnings("ignore", category=UserWarning)
transformers_logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

# ===== FLASK APP SETUP =====
app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

# Ensure OpenAI key exists
app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY missing in .env!")

# ===== BLUEPRINT REGISTRATION =====
app.register_blueprint(auth_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(index_bp)
app.register_blueprint(about_bp)
app.register_blueprint(mental_health_bp)
app.register_blueprint(female_health_bp)
app.register_blueprint(gdpr_bp)


@app.before_request
def enforce_gdpr():
    allowed_endpoints = [
        "gdpr.privacy_notice", "gdpr.consent", "static"
    ]
    if request.endpoint in allowed_endpoints or session.get("gdpr_consent"):
        return  # Allow access

    return redirect(url_for("gdpr.privacy_notice"))



# ===== ROUTE: Home Page =====
@app.route("/")
def home():
    """
    Home route logic.
    Redirects logged-in users to chatbot.
    Shows homepage to non-authenticated users.
    """
    # this is for login the chatbot MAIN PART DONOT CHANGE ANYTHING
    # # Always show the homepage, regardless of session state
    # if "username" in session:
    #    session.clear()  # Clear the session when the homepage is accessed

    # return render_template("index.html")

    # chatbot within login FOR TESTING NOW
    # Redirect logged-in users to the chatbot page
    if "username" in session:
        return redirect(url_for("chatbot.chatbot_page"))
    # Show the homepage for non-logged-in users
    return render_template("index.html")


# ===== ROUTE: 404 Error Page =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# ===== START SERVER =====
if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True, use_reloader=False)
