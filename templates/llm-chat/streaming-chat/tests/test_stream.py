import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from stream import StreamingChatEngine, StreamMode


def test_create_stream_session():
    engine = StreamingChatEngine()
    session = engine.create_stream_session(mode=StreamMode.SSE)
    assert session.session_id in engine.sessions
    assert session.mode == StreamMode.SSE
    assert session.buffer == ""
    assert session.chunk_count == 0
    assert session.complete is False


def test_consume_chunks():
    engine = StreamingChatEngine()
    session = engine.create_stream_session()
    chunk1 = engine.consume_chunk(session.session_id, "Hello")
    chunk2 = engine.consume_chunk(session.session_id, " world", finish_reason="stop")
    assert chunk1.index == 0
    assert chunk1.delta == "Hello"
    assert chunk1.finish_reason is None
    assert chunk2.index == 1
    assert chunk2.finish_reason == "stop"
    assert engine.sessions[session.session_id].buffer == "Hello world"
    assert engine.sessions[session.session_id].complete is True


def test_stream_complete_blocks_further_chunks():
    engine = StreamingChatEngine()
    session = engine.create_stream_session()
    engine.consume_chunk(session.session_id, "done", finish_reason="stop")
    with pytest.raises(ValueError, match="already complete"):
        engine.consume_chunk(session.session_id, "extra")


def test_simulate_stream_builds_full_text():
    engine = StreamingChatEngine()
    session = engine.create_stream_session()
    full_text = "The quick brown fox"
    chunks = list(engine.simulate_stream(session.session_id, full_text))
    assert len(chunks) == 4  # 4 words
    assert chunks[-1].finish_reason == "stop"
    reconstructed = engine.get_full_response(session.session_id)
    assert reconstructed == full_text
