import os
from typing import List

import pytest
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference

load_dotenv()

BASE_URL = "http://localhost:8000"
ASK_ENDPOINT = f"{BASE_URL}/ask"
TOP_K = 3
MIN_CONTEXT_PRECISION_SCORE = 0.7


TEST_CASES = [
    {
        "question": "What is an AI Agent?",
        "reference": (
            "An AI Agent is a software system that can interpret goals, reason over context, "
            "choose actions, and often use tools or memory to complete tasks with limited human intervention."
        ),
    },
    {
        "question": "What is Model Context Protocol?",
        "reference": (
            "Model Context Protocol is a structured way for AI assistants to connect with external tools, "
            "resources, and context providers in a standardized manner."
        ),
    },
    {
        "question": "How does RAG reduce hallucination?",
        "reference": (
            "RAG reduces hallucination by retrieving relevant external context and grounding the generated answer "
            "in that retrieved information instead of relying only on the model's internal memory."
        ),
    },
    {
        "question": "What are the key LLM evaluation metrics?",
        "reference": (
            "Key LLM evaluation metrics include faithfulness, answer relevancy, context precision, and context recall. "
            "These help assess retrieval quality and generation quality in RAG systems."
        ),
    },
    {
        "question": "How can Cypress support AI-powered testing?",
        "reference": (
            "Cypress can support AI-powered testing by validating UI flows, integrating with AI-assisted test generation, "
            "and serving as part of broader quality pipelines that include AI-driven analysis and orchestration."
        ),
    },
]


def get_evaluator_llm() -> LangchainLLMWrapper:
    """
    Create the LLM wrapper used by RAGAS metrics.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file or Run Configuration."
        )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )
    return LangchainLLMWrapper(llm)


def call_ask_api(question: str, top_k: int = TOP_K) -> dict:
    """
    Call the local RAG API /ask endpoint.
    """
    response = requests.post(
        ASK_ENDPOINT,
        json={
            "question": question,
            "chat_history": [],
            "top_k": top_k,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def extract_retrieved_contexts(response_dict: dict) -> List[str]:
    """
    Extract page_content from the API response documents list.
    """
    documents = response_dict.get("documents", [])
    return [doc.get("page_content", "") for doc in documents if doc.get("page_content")]


@pytest.fixture(scope="session")
def evaluator_llm() -> LangchainLLMWrapper:
    """
    Session-level fixture so the evaluator model is created only once.
    """
    return get_evaluator_llm()


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", TEST_CASES)
async def test_context_precision_for_multiple_questions(test_case: dict, evaluator_llm: LangchainLLMWrapper):
    question = test_case["question"]
    reference = test_case["reference"]

    response_dict = call_ask_api(question)

    print(f"\nQuestion: {question}")
    print("API Response:", response_dict)

    # Basic API structure validations
    assert "question" in response_dict, "Missing 'question' in API response"
    assert "answer" in response_dict, "Missing 'answer' in API response"
    assert "documents" in response_dict, "Missing 'documents' in API response"
    assert isinstance(response_dict["documents"], list), "'documents' should be a list"
    assert len(response_dict["documents"]) > 0, "No documents returned from API"
    assert isinstance(response_dict["answer"], str), "'answer' should be a string"
    assert response_dict["answer"].strip() != "", "Answer is empty"

    retrieved_contexts = extract_retrieved_contexts(response_dict)

    assert len(retrieved_contexts) > 0, "No retrieved contexts extracted from API response"

    metric = LLMContextPrecisionWithReference(llm=evaluator_llm)

    sample = SingleTurnSample(
        user_input=question,
        response=response_dict["answer"],
        retrieved_contexts=retrieved_contexts,
        reference=reference,
    )

    score = await metric.single_turn_ascore(sample)

    print(f"Context Precision Score for '{question}': {score}")

    assert score is not None, "Metric score is None"
    assert score >= MIN_CONTEXT_PRECISION_SCORE, (
        f"Context Precision Score too low for question '{question}'. "
        f"Expected >= {MIN_CONTEXT_PRECISION_SCORE}, got {score}"
    )