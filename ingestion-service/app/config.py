import os

# --- Pinecone Config ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "YOUR_PINECONE_API_KEY")
PINECONE_INDEX_NAME = "scheme-ai-index"