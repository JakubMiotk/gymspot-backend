import os
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.documentation import DocumentationCreate, DocumentationOut
from app.services.documentation_service import (
    create_documentation as create_documentation_service,
    get_documentation_by_id,
    get_all_documentation,
    update_documentation as update_documentation_service,
    delete_documentation as delete_documentation_service,
)

UPLOAD_DIR = "uploads/video"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm", "mov", "avi", "mkv"}

router = APIRouter(tags=["documentation"])


@router.post("/documentation", response_model=DocumentationOut)
async def create_documentation(
    exercise_name: str = Form(...),
    exercise_description: Optional[str] = Form(None),
    exercise_type: Optional[str] = Form(None),
    exercise_body_parts: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video_path: Optional[str] = None
    if video and video.filename:
        ext = video.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Nieobsługiwany format wideo")
        filename = f"doc_{uuid.uuid4()}.{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(await video.read())
        video_path = f"/video/{filename}"

    doc_data = DocumentationCreate(
        exercise_name=exercise_name,
        exercise_description=exercise_description,
        exercise_video=video_path,
        exercise_type=exercise_type,
        exercise_body_parts=exercise_body_parts,
        author=current_user.id,
    )
    return create_documentation_service(db, doc_data)


@router.get("/documentation/{doc_id}", response_model=DocumentationOut)
def read_documentation(doc_id: int, db: Session = Depends(get_db)):
    doc = get_documentation_by_id(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Nie znaleziono dokumentacji")
    return doc


@router.get("/documentation", response_model=List[DocumentationOut])
def read_all_documentation(db: Session = Depends(get_db)):
    return get_all_documentation(db)


@router.put("/documentation/{doc_id}", response_model=DocumentationOut)
async def update_existing_documentation(
    doc_id: int,
    exercise_name: str = Form(...),
    exercise_description: Optional[str] = Form(None),
    exercise_type: Optional[str] = Form(None),
    exercise_body_parts: Optional[str] = Form(None),
    video: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = get_documentation_by_id(db, doc_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Nie znaleziono dokumentacji")

    video_path: Optional[str] = existing.exercise_video
    if video and video.filename:
        ext = video.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Nieobsługiwany format wideo")
        filename = f"doc_{uuid.uuid4()}.{ext}"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(await video.read())
        # Usuń stary plik jeśli istnieje
        if existing.exercise_video:
            old_file = existing.exercise_video.lstrip("/video/")
            old_path = os.path.join(UPLOAD_DIR, old_file)
            if os.path.exists(old_path):
                os.remove(old_path)
        video_path = f"/video/{filename}"

    doc_data = DocumentationCreate(
        exercise_name=exercise_name,
        exercise_description=exercise_description,
        exercise_video=video_path,
        exercise_type=exercise_type,
        exercise_body_parts=exercise_body_parts,
        author=current_user.id,
    )
    return update_documentation_service(db, doc_id, doc_data)


@router.delete("/documentation/{doc_id}")
def delete_existing_documentation(doc_id: int, db: Session = Depends(get_db)):
    success = delete_documentation_service(db, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono dokumentacji")
    return {"detail": "Dokumentacja została usunięta"}