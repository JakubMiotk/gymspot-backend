from pydantic import BaseModel, ConfigDict

class RelationBase(BaseModel):
    # Both identifiers reference rows in persons, not users.
    client_id: int
    trainer_id: int


class RelationOut(RelationBase):

    model_config = ConfigDict(from_attributes=True)
