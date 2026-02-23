"""
Multi-Provider LLM Chat Template
==================================
A unified chat interface that routes messages to any supported LLM provider.
Supports: OpenAI, Ollama, Groq, Gemini (all via the connectors/ modules)
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
import uuid

class Provider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GROQ = "groq"
    GEMINI = "gemini"

class Message(BaseModel):
    role: str  # system|user|assistant
    content: str

class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message]
    provider: Provider = Provider.OPENAI
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    metadata: dict = Field(default_factory=dict)

class ChatResponse(BaseModel):
    session_id: str
    message: Message
    provider: Provider
    model: str
    usage: dict = Field(default_factory=dict)
    latency_ms: float = 0.0
    finish_reason: str = "stop"

class ConversationHistory(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    provider: Provider = Provider.OPENAI
    model: str = "gpt-4o-mini"
    system_prompt: Optional[str] = None

class MultiProviderChat:
    """Routes chat requests to the appropriate LLM provider."""

    PROVIDER_MODELS = {
        Provider.OPENAI: ["gpt-4o", "gpt-4o-mini", "o1-preview"],
        Provider.OLLAMA: ["llama3.2", "mistral", "deepseek-r1"],
        Provider.GROQ: ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        Provider.GEMINI: ["gemini-1.5-pro", "gemini-2.0-flash"],
    }

    def __init__(self):
        self.sessions: dict[str, ConversationHistory] = {}

    def create_session(self, provider: Provider = Provider.OPENAI,
                       model: str = "gpt-4o-mini",
                       system_prompt: str | None = None) -> ConversationHistory:
        session = ConversationHistory(provider=provider, model=model, system_prompt=system_prompt)
        if system_prompt:
            session.messages.append(Message(role="system", content=system_prompt))
        self.sessions[session.session_id] = session
        return session

    def add_message(self, session_id: str, role: str, content: str) -> Message:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        msg = Message(role=role, content=content)
        session.messages.append(msg)
        return msg

    def get_session(self, session_id: str) -> ConversationHistory:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    def list_models(self, provider: Provider) -> list[str]:
        return self.PROVIDER_MODELS.get(provider, [])

    def build_request(self, session_id: str, user_message: str) -> ChatRequest:
        session = self.get_session(session_id)
        self.add_message(session_id, "user", user_message)
        return ChatRequest(
            session_id=session_id,
            messages=session.messages,
            provider=session.provider,
            model=session.model,
        )

    def simulate_response(self, request: ChatRequest) -> ChatResponse:
        """Simulate a chat response (replace with real connector call in production)."""
        return ChatResponse(
            session_id=request.session_id,
            message=Message(role="assistant", content=f"[{request.provider}:{request.model}] Response to: {request.messages[-1].content[:50]}"),
            provider=request.provider,
            model=request.model,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            latency_ms=150.0,
        )
