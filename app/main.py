"""
SE4206 - DevOps Multi-Stage Pipeline Demo Application
A minimal Flask web service used to demonstrate Jenkins CI/CD.
"""
import os
from flask import Flask, jsonify

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")
APP_ENV = os.getenv("APP_ENV", "local")


@app.route("/")
def home():
    """Landing endpoint - confirms the app is alive."""
    return jsonify({
        "message": "Hello from the SE4206 Jenkins CI/CD Pipeline!",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "status": "running",
    })


@app.route("/health")
def health():
    """Liveness probe - used by Jenkins smoke test and Docker HEALTHCHECK."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/sum/<a>/<b>")
def sum_numbers(a, b):
    """Tiny piece of business logic to give the test suite something real to verify."""
    try:
        a_int, b_int = int(a), int(b)
    except ValueError:
        return jsonify({"error": "a and b must be integers"}), 400
    return jsonify({"a": a_int, "b": b_int, "result": a_int + b_int})


@app.route("/api/multiply/<a>/<b>")
def multiply_numbers(a, b):
    try:
        a_int, b_int = int(a), int(b)
    except ValueError:
        return jsonify({"error": "a and b must be integers"}), 400
    return jsonify({"a": a_int, "b": b_int, "result": a_int * b_int})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
