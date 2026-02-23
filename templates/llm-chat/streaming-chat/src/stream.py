"""
Streaming Chat Template
========================
Handles streaming token responses from LLM APIs.
Supports SSE (Server-Sent Events) and WebSocket streaming.
"""
from pydantic import BaseModel, Field
from typing import Iterator, AsyncIterator, Optional
from enum import Enum
import uuid

class StreamMode(str, Enum):
    SSE = "sse"
    WEBSOCKET = "websocket"
    GENERATOR = "generator"

class StreamChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    delta: str  # The incremental token(s)
    finish_reason: Optional[str] = None  # None until stream ends
    index: int = 0

class StreamSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mode: StreamMode = StreamMode.GENERATOR
    buffer: str = ""
    chunk_count: int = 0
    complete: bool = False

class StreamingChatEngine:
    """Manages streaming chat sessions."""

    def __init__(self):
        self.sessions: dict[str, StreamSession] = {}

    def create_stream_session(self, mode: StreamMode = StreamMode.GENERATOR) -> StreamSession:
        session = StreamSession(mode=mode)
        self.sessions[session.session_id] = session
        return session

    def consume_chunk(self, session_id: str, delta: str,
                      finish_reason: str | None = None) -> StreamChunk:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Stream session {session_id} not found")
        if session.complete:
            raise ValueError(f"Stream session {session_id} is already complete")
        chunk = StreamChunk(
            session_id=session_id,
            delta=delta,
            finish_reason=finish_reason,
            index=session.chunk_count,
        )
        session.buffer += delta
        session.chunk_count += 1
        if finish_reason == "stop":
            session.complete = True
        return chunk

    def get_full_response(self, session_id: str) -> str:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Stream session {session_id} not found")
        return session.buffer

    def simulate_stream(self, session_id: str, full_text: str) -> Iterator[StreamChunk]:
        """Simulate streaming by yielding words one at a time."""
        words = full_text.split()
        for i, word in enumerate(words):
            delta = word + (" " if i < len(words) - 1 else "")
            finish = "stop" if i == len(words) - 1 else None
            yield self.consume_chunk(session_id, delta, finish)
