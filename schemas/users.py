from typing import Optional
from pydantic import BaseModel, Field


class UsersModel(BaseModel):
    """Modelo para adicionar um novo usuário."""

    name: str = Field(..., description="Nome do usuário")
    password: Optional[str] = Field(default=None, description="Senha do usuário")
    role: str = Field(default=None, description="Papel do usuário")
