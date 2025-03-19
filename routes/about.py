from flask import Blueprint, render_template

# Define the Blueprint
about_bp = Blueprint("about", __name__)


# About Page Route
@about_bp.route("/about")
def about():
    return render_template("about.html")
