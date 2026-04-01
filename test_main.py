import pytest
from ragas.metrics import LLMContextPrecisionWithReference

from test_data import TEST_CASES
from utils import call_ask_api, validate_api_response, build_single_turn_sample

MIN_CONTEXT_PRECISION_SCORE = 0.7


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES)
async def test_context_precision_for_multiple_questions(test_case, evaluator_llm):
    response_dict = call_ask_api(test_case["question"])

    print(f"\nQuestion: {test_case['question']}")
    print("API Response:", response_dict)

    validate_api_response(response_dict)

    sample = build_single_turn_sample(test_case, response_dict)

    metric = LLMContextPrecisionWithReference(llm=evaluator_llm)
    score = await metric.single_turn_ascore(sample)

    print(f"Context Precision Score for '{test_case['question']}': {score}")

    assert score is not None, "Metric score is None"
    assert score >= MIN_CONTEXT_PRECISION_SCORE, (
        f"Context Precision Score too low for question '{test_case['question']}'. "
        f"Expected >= {MIN_CONTEXT_PRECISION_SCORE}, got {score}"
    )