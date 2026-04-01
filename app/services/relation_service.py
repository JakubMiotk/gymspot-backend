from sqlalchemy.orm import Session
from app.models.relation import Relation
from app.core.security import get_password_hash, verify_password

def create_relation(db: Session, client_id: int, trainer_id: int):
    relation = Relation(
        client_id=client_id,
        trainer_id=trainer_id
    )
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation

def get_relation_by_client_id(db: Session, client_id: int):
    return db.query(Relation).filter(Relation.client_id == client_id).all()

def get_relation_by_trainer_id(db: Session, trainer_id: int):
    return db.query(Relation).filter(Relation.trainer_id == trainer_id).all()

def delete_relation(db: Session, client_id: int, trainer_id: int):
    relation = db.query(Relation).filter(
        Relation.client_id == client_id,
        Relation.trainer_id == trainer_id
    ).first()
    if relation:
        db.delete(relation)
        db.commit()
        return True
    return False