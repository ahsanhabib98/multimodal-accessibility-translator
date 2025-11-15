from src.config import get_openai_client

client = get_openai_client()

class _ClientSingleton:
    client = client

client_singleton = _ClientSingleton()
