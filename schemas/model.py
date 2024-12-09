from pydantic import BaseModel, Field


class ModelModel(BaseModel):
    """Modelo para adicionar um novo modelo de veículo."""

    id: str = Field(..., description="Nome do modelo do veículo")
    category: int = Field(..., description="Categoria do veículo")
