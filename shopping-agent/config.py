import os

# Global DATA_MODE setting: 'fake_store' (local) or 'mcp'
DATA_MODE = os.getenv("DATA_MODE", "fake_store").lower().strip()


def set_data_mode(choice: str) -> str:
    """Set global DATA_MODE based on user choice ('1'/'fake_store' or '2'/'mcp')."""
    global DATA_MODE
    clean_choice = choice.strip().lower()

    if clean_choice in {"2", "mcp"}:
        DATA_MODE = "mcp"
    else:
        DATA_MODE = "fake_store"

    os.environ["DATA_MODE"] = DATA_MODE
    return DATA_MODE


def get_data_mode() -> str:
    """Return the currently selected DATA_MODE."""
    return DATA_MODE
