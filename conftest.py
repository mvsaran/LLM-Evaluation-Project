import pytest
from utils import get_evaluator_llm
from test_data import TEST_CASES
from utils import get_embeddings


@pytest.fixture(scope="session")
def evaluator_llm():
    return get_evaluator_llm()

@pytest.fixture(params=TEST_CASES)
def test_case(request):
    return request.param

@pytest.fixture(scope="session")
def embeddings():
    return get_embeddings()