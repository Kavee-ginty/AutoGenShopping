import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Example: https://openrouter.ai/api/v1
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# Model name to use with OpenRouter (set in .env)
MODEL = os.getenv("MODEL")
