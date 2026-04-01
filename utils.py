import os
from typing import Dict, List

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper

load_dotenv()

BASE_URL = "http://localhost:8000"
ASK_ENDPOINT = f"{BASE_URL}/ask"
TOP_K = 3


def get_openai_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing in .env")
    return api_key


def get_evaluator_llm() -> LangchainLLMWrapper:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=get_openai_key(),
    )
    return LangchainLLMWrapper(llm)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=get_openai_key(),
    )


def call_ask_api(question: str, top_k: int = TOP_K) -> Dict:
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


def validate_api_response(response_dict: Dict) -> None:
    assert "question" in response_dict, "Missing 'question' in API response"
    assert "answer" in response_dict, "Missing 'answer' in API response"
    assert "documents" in response_dict, "Missing 'documents' in API response"
    assert isinstance(response_dict["documents"], list), "'documents' should be a list"
    assert len(response_dict["documents"]) > 0, "No documents returned from API"
    assert isinstance(response_dict["answer"], str), "'answer' should be a string"
    assert response_dict["answer"].strip() != "", "Answer is empty"


def extract_retrieved_contexts(response_dict: Dict) -> List[str]:
    documents = response_dict.get("documents", [])
    return [
        doc["page_content"]
        for doc in documents
        if isinstance(doc, dict)
        and "page_content" in doc
        and isinstance(doc["page_content"], str)
        and doc["page_content"].strip()
    ]


def build_single_turn_sample(test_case: Dict, response_dict: Dict) -> SingleTurnSample:
    retrieved_contexts = extract_retrieved_contexts(response_dict)

    assert len(retrieved_contexts) > 0, "No retrieved contexts extracted from API response"

    return SingleTurnSample(
        user_input=test_case["question"],
        response=response_dict["answer"],
        retrieved_contexts=retrieved_contexts,
        reference=test_case["reference"],
    )