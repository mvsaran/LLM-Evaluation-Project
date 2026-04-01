import pytest
from ragas.metrics import ResponseRelevancy

from utils import (
    call_ask_api,
    validate_api_response,
    build_single_turn_sample,
)

MIN_ANSWER_RELEVANCY_SCORE = 0.7


@pytest.mark.asyncio
async def test_answer_relevancy(test_case, evaluator_llm, embeddings):
    response_dict = call_ask_api(test_case["question"])

    print(f"\nQuestion: {test_case['question']}")
    print("API Response:", response_dict)

    validate_api_response(response_dict)
    sample = build_single_turn_sample(test_case, response_dict)

    metric = ResponseRelevancy(
        llm=evaluator_llm,
        embeddings=embeddings,
    )

    score = await metric.single_turn_ascore(sample)

    print(f"Answer Relevancy Score for '{test_case['question']}': {score}")

    assert score is not None, "Answer Relevancy score is None"
    assert score >= MIN_ANSWER_RELEVANCY_SCORE, (
        f"Answer Relevancy Score too low for question '{test_case['question']}'. "
        f"Expected >= {MIN_ANSWER_RELEVANCY_SCORE}, got {score}"
    )