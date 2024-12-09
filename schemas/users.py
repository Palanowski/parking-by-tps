from pydantic import BaseModel, Field


class UsersModel(BaseModel):
    """Modelo para adicionar um novo usuário."""

    name: str = Field(..., description="Nome do usuário")
    password: str = Field(..., description="Senha do usuário")
    role: str = Field(..., description="Papel do usuário")
