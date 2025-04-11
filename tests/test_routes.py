import pytest
from app.main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_ask_route_no_index(client):
    app.config["INDEX"] = None
    response = client.post("/ask", json={"question": "Who is the Archmage?"})
    assert response.status_code == 200
    assert "not yet connected" in response.json["response"]