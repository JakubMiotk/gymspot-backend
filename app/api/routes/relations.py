from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.relation import RelationBase, RelationOut
from app.services.relation_service import create_relation, get_relation_by_client_id, get_relation_by_trainer_id, delete_relation
from app.db.session import get_db

router = APIRouter(tags=["relations"])

# Pobierz relacje dla trenera   
@router.get("/trainer/{trainer_id}", response_model=List[RelationOut])
def read_relations_for_trainer(trainer_id: int, db: Session = Depends(get_db)):
    relations = get_relation_by_trainer_id(db, trainer_id)
    if not relations:
        raise HTTPException(status_code=404, detail="Nie znaleziono relacji dla tego trenera")
    return relations

# Pobierz relacje dla klienta
@router.get("/client/{client_id}", response_model=List[RelationOut])
def read_relations_for_client(client_id: int, db: Session = Depends(get_db)):
    relations = get_relation_by_client_id(db, client_id)
    if not relations:
        raise HTTPException(status_code=404, detail="Nie znaleziono relacji dla tego użytkownika")
    return relations


# Rejestracja relacji
@router.post("/", response_model=RelationOut)
def register_relation(relation: RelationBase, db: Session = Depends(get_db)):
    return create_relation(db, relation.client_id, relation.trainer_id)


# Usunięcie relacji
@router.delete("/")
def remove_relation(relation: RelationBase, db: Session = Depends(get_db)):
    success = delete_relation(db, relation.client_id, relation.trainer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono relacji do usunięcia")
    return {"msg": "Relacja została pomyślnie usunięta"}