# 🧪 LLM Evaluation Harness
### *Because "it returned something" isn't good enough.*

> A lightweight, pytest-powered quality gate for RAG (Retrieval-Augmented Generation) systems — evaluating not just *what* your AI returns, but *whether it should have*.

---

## 🎯 What This Does

This project wraps your local RAG API in a rigorous evaluation layer. It asks questions, collects answers and retrieved documents, and uses an LLM judge to score quality across three critical dimensions:

| Metric | Question It Answers |
|---|---|
| 🎯 **Context Precision** | Did we retrieve the *right* documents? |
| 🔗 **Faithfulness** | Is the answer *grounded* in what was retrieved? |
| 💬 **Response Relevancy** | Did the answer actually *address* the question? |

---

## 🗺️ How It Works

```
📋 Test Question
      ↓
🌐 Local RAG API  (http://localhost:8000/ask)
      ↓
📄 Answer + Retrieved Documents
      ↓
🧱 ragas SingleTurnSample
      ↓
⚖️  LLM Judge (OpenAI-backed)
      ↓
✅ PASS (score ≥ 0.7)  or  ❌ FAIL
```

Think of it like a school exam:
- 🎓 **Your RAG API** = the student
- 📝 **This repo** = the examiner
- 📐 **ragas** = the scoring rubric
- 🤖 **OpenAI evaluator** = the judge

---

## 📦 Dependencies

```bash
pip install langchain-openai pytest ragas requests python-dotenv langchain-community
```

| Package | Role |
|---|---|
| `pytest` | Test runner & orchestration |
| `ragas` | RAG evaluation framework |
| `langchain-openai` | Evaluator LLM + embeddings |
| `requests` | Calls your local RAG API |
| `python-dotenv` | Loads secrets from `.env` |

---

## ⚡ Quick Start

### 1️⃣ Create your environment

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### 2️⃣ Set your API key

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
```

> ⚠️ **Never commit `.env` to version control.** The repo currently has a real-looking key that should be rotated and removed immediately.

### 3️⃣ Start your RAG server

Your API must be running at:
```
http://localhost:8000/ask
```

### 4️⃣ Run the tests

```powershell
# Run everything
pytest

# Run individual tests
pytest test_faithfulness.py
pytest test_context_precision.py
pytest response_relevancy.py
```

---

## 📡 Expected API Contract

Your RAG server must return JSON in this shape:

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

> 🔧 If this shape changes, the extraction logic in `utils.py` needs to be updated.

---

## 🗂️ Project Structure

```
LLMEvaluation/
│
├── 🔧 Configuration
│   ├── .env                    # API keys (DO NOT COMMIT)
│   ├── pyproject.toml          # Project manifest & dependencies
│   ├── pytest.ini              # asyncio_mode = auto
│   └── uv.lock                 # Pinned dependency versions
│
├── 🧪 Core Tests
│   ├── test_context_precision.py   # Is retrieved context relevant?
│   ├── test_faithfulness.py        # Is the answer grounded in context?
│   ├── response_relevancy.py       # Does the answer address the question?
│   └── test_main.py                # Parameterized context precision variant
│
├── 🛠️ Shared Utilities
│   ├── utils.py                # API calls, response parsing, sample builder
│   ├── conftest.py             # Shared pytest fixtures
│   └── test_data.py            # Benchmark questions + reference answers
│
├── 🔬 Experimental / Lab
│   ├── RAGAPI.py               # Early proof-of-concept (single question)
│   ├── parameterizedtests.py   # Self-contained older version
│   └── generate_test_data.py   # Synthetic test data generator
│
└── 📁 Data
    ├── generated_test_data.csv # Output from test data generator
    └── data/sample_docs        # Sample knowledge source content
```

---

## 📖 File Guide — Where to Start

If you're new here, read these files in order:

1. 📄 `README.md` ← you are here
2. ⚙️ `pyproject.toml` — understand the dependencies
3. 🛠️ `utils.py` — the integration heart of the project
4. 🔌 `conftest.py` — shared fixtures
5. 📋 `test_data.py` — the evaluation dataset
6. 🎯 `test_context_precision.py` — retrieval quality check
7. 🔗 `test_faithfulness.py` — hallucination check
8. 💬 `response_relevancy.py` — answer usefulness check

---

## ✅ Strengths

- ✨ Uses **real RAG metrics** — not just string matching
- 🧩 Modular: helpers in `utils.py`, fixtures in `conftest.py`
- 🚀 Easy to extend with new questions or metrics
- 🪶 Small and focused — no unnecessary complexity

---

## ⚠️ Known Issues & Gaps

| # | Issue | Impact |
|---|---|---|
| 🔑 | **Exposed API key in `.env`** | Security risk — rotate immediately |
| 🔁 | **Duplicate context precision tests** across 4 files | Hard to maintain one source of truth |
| 📂 | **Hardcoded external path** in `generate_test_data.py` | Not portable across machines |
| 🚫 | **No `.gitignore`** | `.venv`, `__pycache__`, `.env` may get committed |
| 📛 | **`response_relevancy.py`** doesn't start with `test_` | Inconsistent pytest discovery |

---

## 🛣️ Suggested Next Steps

```
□  Add a .gitignore
□  Rotate and remove the exposed API key
□  Consolidate duplicate context precision tests into one
□  Rename response_relevancy.py → test_response_relevancy.py
□  Point generate_test_data.py at local data/ folder
□  Promote generated_test_data.csv entries into test_data.py
```

---

## 💡 The Big Idea

Most API tests only ask: *"Did it return something?"*

This project asks: *"Did it return the **right** something, for the **right** reasons?"*

That distinction is what separates a reliable RAG system from one that just sounds confident.

---

*Built with `pytest` · `ragas` · `langchain-openai`*
