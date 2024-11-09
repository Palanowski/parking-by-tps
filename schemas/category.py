from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """Modelo para adicionar uma nova categoria de veículo."""

    name: str = Field(..., description="Descrição da categoria")
    value: float = Field(default=0, description="Valor cobrado por hora")
