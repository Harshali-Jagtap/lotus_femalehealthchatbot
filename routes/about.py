# ===== Flask Blueprint: About Page =====
from flask import Blueprint, render_template

# Define the Blueprint for the About section
about_bp = Blueprint("about", __name__)


# ===== Route: /about =====
@about_bp.route("/about")
def about():
    """
    Render the About page.
    """
    return render_template("about.html")
