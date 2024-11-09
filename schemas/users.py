from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """Modelo para adicionar um novo usuário."""

    name: str = Field(..., description="Descrição da categoria")
    password: str = Field(..., description="Valor cobrado por hora")
