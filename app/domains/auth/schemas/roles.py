from uuid import UUID
from typing import List
from pydantic import BaseModel, Field, field_validator


class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=50, example="admin")

    @field_validator('name')
    def name_must_not_be_empty(cls, value):
        if not value or value.isspace() or (value.lower() == 'string'):
            raise ValueError("Role name must not be empty or only whitespace or string")
        return value


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50, example="admin")

class RoleUpdate(RoleBase):
    pass


class RoleSchema(RoleBase):
    id: UUID
    name: str


    class Config:
        from_attributes = True



class RoleResponse(BaseModel):
    bk_size: int
    pg_size: int
    data: List[RoleSchema]