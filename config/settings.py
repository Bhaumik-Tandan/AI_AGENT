import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
API_VERSION = "v1"
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 6000))

# Database Settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agent_builder.db")

# OpenAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# RAG Settings
EMBEDDING_MODEL = "text-embedding-ada-002"
VECTOR_SIMILARITY_THRESHOLD = 0.8

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")