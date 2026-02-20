# LLM Chat Templates

This category contains templates for building chat interfaces powered by large language models (LLMs).

## Templates

- **multi-provider-chat** — Unified chat interface that routes messages to OpenAI, Ollama, Groq, or Gemini via the `connectors/` modules. Supports session management and conversation history.
- **streaming-chat** — Minimal template for consuming streaming token responses using SSE, WebSocket, or Python generators.

## Usage

Each template is self-contained with `src/`, `tests/`, `requirements.txt`, and a `Dockerfile`. Install dependencies with `pip install -r requirements.txt` and run tests with `pytest`.

## Design Principles

- Provider-agnostic: swap LLM backends without changing application logic.
- Pydantic models for all request/response contracts.
- Drop-in integration with `connectors/` modules from this repository.
