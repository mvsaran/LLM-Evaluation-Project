import pytest
from ragas.metrics import Faithfulness

from utils import call_ask_api, validate_api_response, build_single_turn_sample

MIN_FAITHFULNESS_SCORE = 0.7


@pytest.mark.asyncio
async def test_faithfulness(test_case, evaluator_llm):
    response_dict = call_ask_api(test_case["question"])

    print(f"\nQuestion: {test_case['question']}")
    print("API Response:", response_dict)

    validate_api_response(response_dict)
    sample = build_single_turn_sample(test_case, response_dict)

    metric = Faithfulness(llm=evaluator_llm)
    score = await metric.single_turn_ascore(sample)

    print(f"Faithfulness Score for '{test_case['question']}': {score}")

    assert score is not None, "Faithfulness score is None"
    assert score >= MIN_FAITHFULNESS_SCORE, (
        f"Faithfulness Score too low for question '{test_case['question']}'. "
        f"Expected >= {MIN_FAITHFULNESS_SCORE}, got {score}"
    )