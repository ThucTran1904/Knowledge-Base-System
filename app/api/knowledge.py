from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_session
from app.db.models import Document
from app.services.embedder import embed_text
from sqlalchemy import delete

from pydantic import BaseModel
from typing import List
from sqlalchemy import text
from datetime import datetime 

import uuid, time
from fastapi.responses import StreamingResponse
from app.db.models import AuditLog


router = APIRouter()

class DocIn(BaseModel):
    documents: List[str]
    
class QueryIn(BaseModel):
    query: str

@router.post("/knowledge/update")
async def update_knowledge(data: DocIn, session: AsyncSession = Depends(get_session)):
    try: 
        
        embeddings = embed_text(data.documents)

        if not embeddings or not isinstance(embeddings[0], list):
            raise ValueError("Embedding failed or returned invalid format")

        for content, vector in zip(data.documents, embeddings):
            doc = Document(content=content, embedding=vector)
            session.add(doc)
            
        await session.commit()
        return {"status": "success", "count": len(data.documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")



@router.post('/knowledge/query')
async def query_knowledge(data: QueryIn, session: AsyncSession = Depends(get_session)):
    try: 
        embedding_list = embed_text(data.query)
        
        if not embedding_list or not isinstance(embedding_list[0], list):
            raise ValueError("Embedding failed or returned invalid format")
        
        embedding = embedding_list[0]
    
        stmt = select(Document).order_by(Document.embedding.l2_distance(embedding)).limit(3)
        result = await session.execute(stmt)
        documents = result.scalars().all()
        
        return {"query": data.query, "results": [doc.content for doc in documents]}
    except Exception as e:
        return {"error": str(e)}

@router.delete("/knowledge/reset")
async def reset_knowledge(session: AsyncSession = Depends(get_session)):
    await session.execute(delete(Document))
    await session.commit()
    return {"status": "reset successful"}
    
@router.delete("/knowledge/{id}")
async def delete_document(id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document).where(Document.id == id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await session.delete(doc)
    await session.commit()
    return {"status":"delete","id":id}

@router.get("/knowledge")
async def list_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document))
    documents = result.scalars().all()
    return [
        {
            "id": doc.id,
            "size": len(doc.content),
            "created_at": doc.created_at.isoformat() if isinstance(doc.created_at, datetime) else str(doc.created_at)
        }
        for doc in documents
    ]

@router.get('/health')
async def health(session: AsyncSession = Depends(get_session)):
    try:
        await session.execute(text('SELECT 1'))
        return {"status":"ok"}
    except Exception as e:
        return {"status": "error", "details":str(e)}
    
