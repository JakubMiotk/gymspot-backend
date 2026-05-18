import os
from sqlalchemy.orm import Session
from app.schemas.documentation import DocumentationCreate
from app.models.documentation import Documentation

def create_documentation(db: Session, documentation_data: DocumentationCreate):
    documentation = Documentation(
        exercise_name=documentation_data.exercise_name,
        exercise_description=documentation_data.exercise_description,
        exercise_video=documentation_data.exercise_video,
        exercise_type=documentation_data.exercise_type,
        exercise_body_parts=documentation_data.exercise_body_parts,
        author=documentation_data.author
    )
    db.add(documentation)
    db.commit()
    db.refresh(documentation)
    return documentation

def get_documentation_by_id(db: Session, documentation_id: int):
    return db.query(Documentation).filter(Documentation.id == documentation_id).first()

def get_all_documentation(db: Session):
    return db.query(Documentation).all()

def update_documentation(db: Session, documentation_id: int, update_data: DocumentationCreate):
    documentation = db.query(Documentation).filter(Documentation.id == documentation_id).first()
    if not documentation:
        return None
    documentation.exercise_name = update_data.exercise_name
    documentation.exercise_description = update_data.exercise_description
    documentation.exercise_video = update_data.exercise_video
    documentation.exercise_type = update_data.exercise_type
    documentation.exercise_body_parts = update_data.exercise_body_parts
    documentation.author = update_data.author

    db.commit()
    db.refresh(documentation)
    return documentation

def delete_documentation(db: Session, documentation_id: int):
    documentation = db.query(Documentation).filter(Documentation.id == documentation_id).first()
    if documentation:
        if documentation.exercise_video:
            video_file = documentation.exercise_video.lstrip("/video/")
            video_path = os.path.join("uploads/video", video_file)
            if os.path.exists(video_path):
                os.remove(video_path)
        db.delete(documentation)
        db.commit()
        return True
    return False