# LLM Evaluation Project

This project is a small evaluation harness for a Retrieval-Augmented Generation (RAG) application.

In simple terms, it asks questions to a local AI API, collects the answer and the supporting documents the API retrieved, and then uses another model to judge whether the response was good enough.

The goal is to help you answer questions like:

- Did the RAG system retrieve the right information?
- Did the answer stay grounded in the retrieved documents?
- Did the answer actually address the question?

## Highlights

- [*] Evaluates a local RAG API instead of building one
- [*] Checks retrieval quality, grounding, and answer usefulness
- [*] Uses `pytest`, `ragas`, and OpenAI-backed evaluators
- [*] Keeps the workflow small and easy to extend

## What This Project Does

The project assumes you already have a local RAG server running at `http://localhost:8000` with an `/ask` endpoint.

For each test question, this repository:

1. Sends the question to the local RAG API.
2. Receives an answer plus retrieved documents.
3. Converts that API response into a format understood by `ragas`.
4. Scores the result using evaluation metrics such as:
   - Context Precision
   - Faithfulness
   - Response Relevancy
5. Fails the test if the score is below the chosen threshold.

This makes the repository useful as a lightweight quality gate for a RAG application.

## Project In Plain Language

Think of the setup like this:

- Your RAG API is the student answering exam questions.
- This repository is the examiner.
- `ragas` is the scoring rubric.
- The OpenAI evaluator model is the judge that helps score the answers.

So instead of only checking whether the API returned "something," this project checks whether it returned something trustworthy and useful.

## How The Flow Works

1. [>] A pytest test starts.
2. [>] A question is picked from `test_data.py`.
3. [>] The test calls the local `/ask` API.
4. [>] The returned `documents` are extracted as retrieved context.
5. [>] A `SingleTurnSample` is built for `ragas`.
6. [>] A metric computes a score.
7. [>] The test passes only if the score is at or above the minimum threshold.

## Main Dependencies

- [pkg] `pytest`: test runner
- [pkg] `requests`: calls the local RAG API
- [pkg] `ragas`: evaluation framework for RAG systems
- [pkg] `langchain-openai`: connects the evaluator model and embeddings

## Expected API Contract

The tests assume the local API returns JSON with at least these fields:

```json
{
  "question": "user question",
  "answer": "model answer",
  "documents": [
    {
      "page_content": "retrieved supporting text"
    }
  ]
}
```

If the API shape changes, the tests will fail until the extraction logic is updated.

## Setup

### 1. Create the environment

This repo uses `uv` style lock metadata, but you can also use plain `pip`.

Example:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Or install directly from the declared dependencies:

```powershell
pip install langchain-openai pytest ragas requests python-dotenv langchain-community
```

### 2. Add environment variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_key_here
```

Important:

- [!] The current repository already contains a real-looking API key in `.env`.
- [!] That key should be rotated immediately and removed from version control.
- [!] `.env` should normally be ignored by Git.

### 3. Start the local RAG API

The tests expect a running server at:

```text
http://localhost:8000/ask
```

### 4. Run the tests

```powershell
pytest
```

You can also run a specific file:

```powershell
pytest test_faithfulness.py
pytest test_context_precision.py
pytest response_relevancy.py
```

## Project Structure

This is the practical structure of the repo, before diving into what each file does:

```text
LLMEvaluation/
|-- .env
|-- conftest.py
|-- generate_test_data.py
|-- generated_test_data.csv
|-- parameterizedtests.py
|-- pyproject.toml
|-- pytest.ini
|-- RAGAPI.py
|-- response_relevancy.py
|-- test_context_precision.py
|-- test_data.py
|-- test_faithfulness.py
|-- test_main.py
|-- utils.py
|-- uv.lock
|-- data/
|   `-- sample_docs
|-- .idea/
|-- .pytest_cache/
|-- __pycache__/
`-- .venv/
```

## Structure At A Glance

- [cfg] Configuration and dependency files: `.env`, `pyproject.toml`, `pytest.ini`, `uv.lock`
- [test] Main evaluation logic: `test_context_precision.py`, `test_faithfulness.py`, `response_relevancy.py`, `test_main.py`
- [data] Test inputs and generated artifacts: `test_data.py`, `generated_test_data.csv`, `data/sample_docs`
- [util] Shared helpers and fixtures: `utils.py`, `conftest.py`
- [lab] Experimental or earlier scripts: `RAGAPI.py`, `parameterizedtests.py`, `generate_test_data.py`
- [tool] Local tooling and generated folders: `.idea/`, `.pytest_cache/`, `__pycache__/`, `.venv/`

## File-By-File Explanation

### [cfg] Core Project Files

#### `pyproject.toml`

This is the project manifest.

What it does here:

- Defines the project name and version.
- Declares the Python version requirement (`>=3.13`).
- Lists the main packages needed to run the evaluation project.

Why it matters:

- This is the starting point for recreating the environment.

#### `uv.lock`

This is the dependency lock file created by `uv`.

What it does here:

- Pins exact package versions so the environment can be reproduced more consistently.

Why it matters:

- Without a lock file, two machines can install slightly different versions and produce slightly different behavior.

#### `pytest.ini`

This file configures pytest.

What it does here:

- Sets `asyncio_mode = auto`, which helps pytest handle async tests without extra manual setup.

Why it matters:

- Several evaluation tests are async because `ragas` metric scoring is async.

#### `.env`

This file stores local environment variables.

What it does here:

- Supplies `OPENAI_API_KEY`, which is required for the evaluator LLM and embeddings.

Why it matters:

- The tests do not only call your local API; they also call OpenAI-backed evaluation components through `langchain-openai`.

Risk:

- This file should not contain a committed secret in a shared repository.

### [util] Test Support Files

#### `utils.py`

This is the main shared helper module and one of the most important files in the repo.

What it does here:

- Loads the API key from the environment.
- Creates the evaluator LLM wrapper.
- Creates the embeddings model used by response relevancy scoring.
- Calls the local `/ask` API.
- Validates that the API response has the expected structure.
- Extracts retrieved document text.
- Builds the `SingleTurnSample` object used by `ragas`.

Why it matters:

- It removes repeated code from the tests and acts as the central integration layer.

#### `conftest.py`

This file contains pytest fixtures shared across tests.

What it does here:

- Creates the evaluator LLM once per test session.
- Creates embeddings once per test session.
- Supplies one test case at a time from `TEST_CASES`.

Why it matters:

- Keeps the tests cleaner.
- Avoids repeatedly recreating expensive model clients.

#### `test_data.py`

This file defines the evaluation questions and their reference answers.

What it does here:

- Stores the small benchmark set used by the tests.
- Gives each question a reference statement that represents a good grounded answer.

Why it matters:

- This is effectively the mini evaluation dataset for the project.

### [test] Main Evaluation Tests

#### `test_context_precision.py`

This test checks whether the retrieved documents are actually relevant to the question and reference answer.

What it does here:

- Sends each test question to the local API.
- Validates the API response format.
- Builds a `ragas` sample.
- Scores it using `LLMContextPrecisionWithReference`.
- Fails if the score is below `0.7`.

Why it matters:

- In a RAG system, good answers depend on good retrieval.
- If the wrong context is retrieved, the final answer is likely to be weak.

#### `test_faithfulness.py`

This test checks whether the answer is supported by the retrieved documents instead of being invented.

What it does here:

- Uses the `Faithfulness` metric from `ragas`.
- Fails when the answer is not sufficiently grounded in the retrieved context.

Why it matters:

- This is one of the most important checks for hallucination control.

#### `response_relevancy.py`

Despite the name, this is also a pytest test file.

What it does here:

- Measures whether the API answer actually responds to the user’s question.
- Uses `ResponseRelevancy` from `ragas`.
- Requires both the evaluator LLM and embeddings.

Why it matters:

- A response can be factually grounded and still not answer the question properly.

#### `test_main.py`

This is another context precision test, but written using explicit parameterization over `TEST_CASES`.

What it does here:

- Repeats the context precision evaluation logic with `@pytest.mark.parametrize`.

Why it matters:

- It appears to be a cleaner or alternate version of the same idea found in `test_context_precision.py`.
- In practice, this overlaps with `test_context_precision.py` and may be redundant.

### [lab] Additional / Older / Experimental Files

#### `RAGAPI.py`

This is a standalone test script focused on context precision for one hardcoded question.

What it does here:

- Calls the local API directly.
- Builds a `SingleTurnSample`.
- Runs one context precision check for `"How does RAG reduce hallucination?"`

Why it matters:

- It looks like an early proof-of-concept before the shared utility and fixture pattern was introduced.

Current role:

- Useful as a simple example, but largely superseded by the more structured pytest files.

#### `parameterizedtests.py`

This file combines multiple concerns in one script.

What it does here:

- Defines test cases locally.
- Defines helper functions locally.
- Defines an evaluator fixture.
- Runs a parameterized context precision test.

Why it matters:

- It appears to be an earlier self-contained version of the project before code was split into `utils.py`, `conftest.py`, and `test_data.py`.

Current role:

- Mostly redundant with the current modular structure.

#### `generate_test_data.py`

This script tries to generate synthetic evaluation data automatically.

What it does here:

- Loads documents from a docs folder.
- Uses `ragas.testset.TestsetGenerator`.
- Produces a CSV of generated test questions and references.

Why it matters:

- It can help you grow the evaluation dataset instead of hand-writing every test case.

Important limitation:

- It uses a hardcoded path outside this repository:
  `C:\Users\mvsar\Projects\RAGAPISERVER\data\docs`
- That means it is not portable as-is.

#### `generated_test_data.csv`

This is the output from the test-data generator.

What it does here:

- Stores generated prompts, references, personas, and synthesis metadata.

Why it matters:

- It can serve as raw material for expanding `test_data.py` or building a richer benchmark later.

### [data] Data Folder

#### `data/sample_docs`

This is a local sample knowledge file used as example source content.

What it does here:

- Contains short plain-text explanations about RAG, MCP, AI agents, LLM evaluation, and Cypress.

Why it matters:

- It represents the kind of source material a RAG system would index and retrieve from.

Note:

- The file has no `.txt` extension.
- `generate_test_data.py` currently loads `*.txt` files from a different external path, so this local file is not being used by that script right now.

### [tool] Tooling / Generated Folders

#### `.idea/`

PyCharm project settings.

What it does here:

- Stores IDE-specific configuration.

Why it matters:

- Helpful for local development in PyCharm.
- Not important for the runtime behavior of the evaluation project itself.

#### `.pytest_cache/`

Pytest cache data.

What it does here:

- Stores test run metadata to speed up repeated pytest operations.

Why it matters:

- Convenience only. Not part of the core project logic.

#### `__pycache__/`

Python bytecode cache.

What it does here:

- Stores compiled Python cache files.

Why it matters:

- Generated automatically. Not source code.

#### `.venv/`

Local virtual environment.

What it does here:

- Contains the project’s installed packages and interpreter state.

Why it matters:

- Necessary for local execution, but usually should not be committed to source control.

## Which Files Matter Most

If someone is new to the project, these are the most important files to read first:

1. [1] `README.md`
2. [2] `pyproject.toml`
3. [3] `utils.py`
4. [4] `conftest.py`
5. [5] `test_data.py`
6. [6] `test_context_precision.py`
7. [7] `test_faithfulness.py`
8. [8] `response_relevancy.py`

These files explain almost the entire working system.

## Current Design Strengths

- [+] Simple and easy to understand
- [+] Uses real RAG evaluation metrics instead of only string matching
- [+] Reuses helpers through `utils.py`
- [+] Reuses pytest fixtures through `conftest.py`
- [+] Small benchmark dataset makes iteration easy

## Current Gaps And Practical Issues

### [!] 1. Secret management problem

The repository currently includes a real-looking API key in `.env`.

Why this matters:

- This is a security issue.
- Keys should be rotated and removed from Git history if the repository is shared.

### [!] 2. Duplicate test logic

There are multiple files doing similar context precision checks:

- `RAGAPI.py`
- `parameterizedtests.py`
- `test_context_precision.py`
- `test_main.py`

Why this matters:

- It is harder to maintain one source of truth.

### [!] 3. Hardcoded external document path

`generate_test_data.py` points to a docs folder outside the repository.

Why this matters:

- Another developer cannot run it without editing the script.

### [!] 4. Missing `.gitignore`

There is no visible `.gitignore` at the repo root.

Why this matters:

- Generated folders like `.venv`, `__pycache__`, `.pytest_cache`, and `.env` are usually not committed.

### [!] 5. File naming inconsistency

`response_relevancy.py` is a test file but does not start with `test_`.

Why this matters:

- Depending on pytest discovery rules, naming can become confusing.

## Suggested Next Cleanup Steps

If you want to improve the repository after this README, the best next steps are:

1. [>] Add a `.gitignore`.
2. [>] Remove and rotate the exposed API key.
3. [>] Keep only one context precision test style.
4. [>] Rename `response_relevancy.py` to `test_response_relevancy.py`.
5. [>] Make `generate_test_data.py` read from the local `data/` folder instead of an external hardcoded path.
6. [>] Convert `generated_test_data.csv` into curated test cases for `test_data.py`.

## Summary

This project is a focused testing layer for a local RAG application.

It does not build the RAG system itself. Instead, it checks whether that system is retrieving the right supporting content and producing answers that are grounded, relevant, and reliable.

For a small repository, it already captures an important real-world idea: evaluating AI systems should go beyond "did it return a response?" and move toward "did it return the right response for the right reasons?"
