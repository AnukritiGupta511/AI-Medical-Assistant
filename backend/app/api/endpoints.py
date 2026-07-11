from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from fastapi.responses import Response
from app.api.deps import get_current_user, get_db
from app.models.base import User, MedicalReport, ChatHistory
from app.services.ocr_service import ocr_service
from app.services.llm_service import llm_service
from app.utils.pdf_generator import generate_health_summary_pdf
import shutil
import os

router = APIRouter()

@router.post("/upload")
async def upload_medical_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload a medical report for OCR processing and summarization.
    """
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.docx'}
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Save file temporarily
    os.makedirs("temp_uploads", exist_ok=True)
    file_path = f"temp_uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Run OCR
        extracted_text = await ocr_service.extract_text(file_path, file.content_type)
        
        # Save to DB
        report = MedicalReport(
            owner_id=current_user.id,
            filename=file.filename,
            original_file_path=file_path,
            extracted_text=extracted_text,
            status="completed"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return {
            "report_id": report.id,
            "filename": file.filename,
            "status": "completed",
            "message": "File processed successfully via OCR."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []

@router.post("/chat")
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Chat with the AI Medical Assistant using RAG.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    # Run LangGraph LLM processing
    try:
        result = llm_service.process_query(request.query, request.history)
        
        # Store in ChatHistory DB
        chat_log = ChatHistory(
            owner_id=current_user.id,
            query=request.query,
            response=result["response"],
            confidence_score=result.get("confidence_score"),
            citations=str(result.get("citations", []))
        )
        db.add(chat_log)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/report/download')
async def download_health_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate and download a comprehensive PDF health summary report.
    """
    reports = db.query(MedicalReport).filter(MedicalReport.owner_id == current_user.id).all()
    chat_logs = db.query(ChatHistory).filter(ChatHistory.owner_id == current_user.id).order_by(ChatHistory.created_at.asc()).all()
    
    pdf_bytes = generate_health_summary_pdf(current_user.email, chat_logs, reports)
    
    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=health_summary_{current_user.id}.pdf'}
    )
