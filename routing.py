# routing.py

from flask import Blueprint, render_template, request, jsonify
from processor import process_data

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    result = process_data(data)
    return jsonify(result)