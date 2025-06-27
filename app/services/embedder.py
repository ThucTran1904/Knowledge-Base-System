import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

google_api_key = os.getenv("GEMINI_API_KEY")
if not google_api_key:
    raise RuntimeError('GEMINI_API_KEY not set in environment')



embedding_model = GoogleGenerativeAIEmbeddings(
    model='models/embedding-001',
    google_api_key=google_api_key
)

def embed_text(texts: list[str]) -> list[list[float]]:
    return embedding_model.embed_documents(texts)