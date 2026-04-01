import os
import pytest
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference

load_dotenv()

@pytest.mark.asyncio
async def test_context_precision():
    question = "How does RAG reduce hallucination?"

    response_dict = requests.post(
        "http://localhost:8000/ask",
        json={
            "question": question,
            "chat_history": [],
            "top_k": 3
        },
        timeout=30
    ).json()

    print(response_dict)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    langchain_llm = LangchainLLMWrapper(llm)
    context_precision = LLMContextPrecisionWithReference(llm=langchain_llm)

    retrieved_contexts = [
        doc["page_content"]
        for doc in response_dict.get("documents", [])
    ]

    sample = SingleTurnSample(
        user_input=question,
        response=response_dict["answer"],
        retrieved_contexts=retrieved_contexts,
        reference=(
            "RAG reduces hallucination by retrieving relevant external context "
            "and grounding the generated answer in that retrieved information "
            "instead of relying only on the model's parametric memory."
        )
    )

    score = await context_precision.single_turn_ascore(sample)
    print("Context Precision Score:", score)

    assert score is not None
    assert score >= 0.7