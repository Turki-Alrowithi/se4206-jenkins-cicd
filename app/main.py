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


@app.route("/api/sum/<int:a>/<int:b>")
def sum_numbers(a, b):
    """Tiny piece of business logic to give the test suite something real to verify."""
    return jsonify({"a": a, "b": b, "result": a + b})


@app.route("/api/multiply/<int:a>/<int:b>")
def multiply_numbers(a, b):
    return jsonify({"a": a, "b": b, "result": a * b})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
