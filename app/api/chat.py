from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.db.models import AuditLog

from fastapi.responses import StreamingResponse
from app.db.models import Document
from app.services.embedder import embed_text
from app.services.gemini import stream_gemini
from pydantic import BaseModel
import uuid, time
from fastapi import APIRouter
from fastapi import BackgroundTasks

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


router = APIRouter()

class ChatQuery(BaseModel):
    query: str

@router.get("/audit/{chat_id}")
async def get_audit(chat_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(AuditLog).where(AuditLog.chat_id == chat_id))
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail='Chat not Found')
    
    return {
        "chat_id": log.chat_id,
        "user_input": log.user_input,
        "retrieved_context": log.retrieved_context,
        "model_output": log.model_output,
        "latency_ms": log.latency_ms,
        "timestamp": log.timestamp.isoformat(),
        "confidence": log.confidence,
        'feedback': log.feedback
    } 
    
@router.post("/chat")
async def chat(data: ChatQuery, session: AsyncSession = Depends(get_session)):
    start = time.time()
    embedding = embed_text(data.query)[0]
    
    # Retrieve top 3 relevant docs
    stmt = select(Document).order_by(Document.embedding.l2_distance(embedding)).limit(3)
    result = await session.execute(stmt)
    documents = result.scalars().all()
    context ="\n\n".join([doc.content for doc in documents])
    
    # Prompt for Gemnini 
    full_prompt = f"Context:\n{context}\n\nUser Query:\n{data.query}" 
    
    # Generate a unique ID for audit
    chat_id = str(uuid.uuid4())
    collected_response = ""
    async def token_stream():
        nonlocal collected_response
        async for chunk in stream_gemini(full_prompt):
            collected_response += chunk
            yield chunk
        
        latency = (time.time() - start) * 1000
        audit = AuditLog(
            chat_id=chat_id,
            user_input=data.query,
            retrieved_context=context, 
            model_output=collected_response,
            latency_ms=latency,
            confidence=confidence,
            feedback=feedback       
        )
        session.add(audit)
        await session.commit()
    return StreamingResponse(token_stream(), media_type="text/event-stream")



    
    


