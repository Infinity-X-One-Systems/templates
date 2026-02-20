# Multi-Provider Chat

A unified Python chat interface that routes messages to OpenAI, Ollama, Groq, or Gemini.
Manages conversation sessions and history with Pydantic-validated request/response models.
Swap providers without changing application logic; replace `simulate_response` with a real `connectors/` call to go live.
