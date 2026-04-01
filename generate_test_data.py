import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.testset import TestsetGenerator

load_dotenv()


def generate_test_data():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env")

    docs_path = Path(r"C:\Users\mvsar\Projects\RAGAPISERVER\data\docs")

    loader = DirectoryLoader(
        str(docs_path),
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()

    print(f"Loaded {len(docs)} documents")

    if not docs:
        raise ValueError("No documents loaded from docs folder")

    for i, doc in enumerate(docs[:3]):
        print(f"\n--- DOC {i+1} PREVIEW ---")
        print(doc.page_content[:400])

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key,
    )
    llm_wrapper = LangchainLLMWrapper(llm)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=api_key,
    )
    embedding_wrapper = LangchainEmbeddingsWrapper(embeddings)

    generator = TestsetGenerator(
        llm=llm_wrapper,
        embedding_model=embedding_wrapper,
    )

    testset = generator.generate_with_langchain_docs(
        docs,
        testset_size=3,
    )

    df = testset.to_pandas()

    print("\nGenerated Test Data:")
    print(df)

    if df.empty:
        print("\nNo rows were generated. Try using richer documents or reducing testset_size further.")
    else:
        df.to_csv("generated_test_data.csv", index=False)
        print("\nSaved to generated_test_data.csv")


if __name__ == "__main__":
    generate_test_data()