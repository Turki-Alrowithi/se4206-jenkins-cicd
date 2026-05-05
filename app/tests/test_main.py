"""
Unit tests for the Flask app.
Run locally with:    pytest app/tests/ -v
Jenkins runs them in the 'Test' stage.
"""
import pytest
from app.main import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_home_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_payload_shape(client):
    data = client.get("/").get_json()
    assert "message" in data
    assert data["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_sum_positive(client):
    response = client.get("/api/sum/2/3")
    assert response.status_code == 200
    assert response.get_json()["result"] == 5


def test_sum_negative(client):
    response = client.get("/api/sum/-5/3")
    assert response.get_json()["result"] == -2


def test_multiply(client):
    response = client.get("/api/multiply/4/5")
    assert response.get_json()["result"] == 20


# ---------------------------------------------------------------------------
# DEMO TIP: To prove the pipeline really stops on test failure, uncomment
# the test below in your live demo. Jenkins will fail at the 'Test' stage
# and the 'Package' / 'Deploy' stages will never execute.
# ---------------------------------------------------------------------------
# def test_intentional_failure_for_demo(client):
#     response = client.get("/api/sum/2/2")
#     assert response.get_json()["result"] == 5  # 2+2 != 5 -> FAILS on purpose
