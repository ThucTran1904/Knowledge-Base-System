from fastapi import FastAPI
from app.api.knowledge import router as knowledge_router
from app.api import chat

app = FastAPI()

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Knowledge Base API running"}

# Register your knowledge endpoints
app.include_router(knowledge_router)
app.include_router(chat.router)

