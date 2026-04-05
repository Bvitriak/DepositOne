from flask import render_template
from core_service.app.about_data import load_about_data

def register_public_routes(app):
    @app.route("/", endpoint="index")
    def index():
        return render_template("index.html")

    @app.route("/about", endpoint="about")
    def about():
        about_data = load_about_data()
        return render_template("about.html", about=about_data)
