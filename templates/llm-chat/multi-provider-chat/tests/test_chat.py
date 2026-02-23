import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat import MultiProviderChat, Provider, Message


def test_create_session_with_system_prompt():
    chat = MultiProviderChat()
    session = chat.create_session(
        provider=Provider.OPENAI,
        model="gpt-4o-mini",
        system_prompt="You are a helpful assistant.",
    )
    assert session.session_id in chat.sessions
    assert len(session.messages) == 1
    assert session.messages[0].role == "system"
    assert session.messages[0].content == "You are a helpful assistant."
    assert session.provider == Provider.OPENAI


def test_add_message_updates_history():
    chat = MultiProviderChat()
    session = chat.create_session()
    chat.add_message(session.session_id, "user", "Hello!")
    chat.add_message(session.session_id, "assistant", "Hi there!")
    history = chat.get_session(session.session_id)
    assert len(history.messages) == 2
    assert history.messages[0].role == "user"
    assert history.messages[1].role == "assistant"


def test_build_request():
    chat = MultiProviderChat()
    session = chat.create_session(provider=Provider.GROQ, model="llama-3.3-70b-versatile")
    request = chat.build_request(session.session_id, "What is the capital of France?")
    assert request.provider == Provider.GROQ
    assert request.model == "llama-3.3-70b-versatile"
    assert request.messages[-1].role == "user"
    assert "France" in request.messages[-1].content
    assert request.session_id == session.session_id


def test_list_models():
    chat = MultiProviderChat()
    openai_models = chat.list_models(Provider.OPENAI)
    assert "gpt-4o" in openai_models
    assert "gpt-4o-mini" in openai_models

    ollama_models = chat.list_models(Provider.OLLAMA)
    assert "llama3.2" in ollama_models

    groq_models = chat.list_models(Provider.GROQ)
    assert "llama-3.3-70b-versatile" in groq_models

    gemini_models = chat.list_models(Provider.GEMINI)
    assert "gemini-1.5-pro" in gemini_models
