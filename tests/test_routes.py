import pytest
from app.main import app
from unittest.mock import MagicMock

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_ask_route_no_index(client):
    app.config["INDEX"] = None
    response = client.post("/ask", json={"question": "Who is the Archmage?"})
    assert response.status_code == 200
    assert "not yet connected" in response.json["response"]

def test_openai_completions_success(client):
    class MockDoc:
        def __init__(self, text):
            self.text = text

    class MockRetriever:
        def retrieve(self, query):
            return [MockDoc("Lore about the Archmage.")]

    mock_index = MagicMock()
    mock_index.as_retriever.return_value = MockRetriever()

    app.config["INDEX"] = mock_index

    response = client.post("/v1/chat/completions", json={
        "model": "elesh-archivist",
        "messages": [
            {"role": "user", "content": "Who is the Archmage?"}
        ]
    })

    assert response.status_code == 200
    assert "choices" in response.json
    assert "message" in response.json["choices"][0]
    assert "content" in response.json["choices"][0]["message"]
