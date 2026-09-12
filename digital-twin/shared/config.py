import os
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CONTROL_LAYER_URL = os.getenv("CONTROL_LAYER_URL", "http://localhost:8001")
BRAIN_PORT = int(os.getenv("BRAIN_PORT", "8000"))