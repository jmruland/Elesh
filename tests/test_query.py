import pytest
from app.query import ask_archivist
from unittest.mock import MagicMock

class MockDoc:
    def __init__(self, text):
        self.text = text

class MockRetriever:
    def retrieve(self, query):
        return [MockDoc("Sample lore content relevant to query")]  # simple mock

def test_ask_archivist():
    mock_index = MagicMock()
    mock_index.as_retriever.return_value = MockRetriever()

    response = ask_archivist("What is the capital of Arden?", mock_index)
    assert isinstance(response, str)
    assert len(response) > 0
