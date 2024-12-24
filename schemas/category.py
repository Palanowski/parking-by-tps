from typing import Optional
from pydantic import BaseModel, Field


class CategoryModel(BaseModel):
    """Modelo para adicionar uma nova categoria de veículo."""

    id: str = Field(..., description="Descrição da categoria")
    price: Optional[float] = Field(default=None, description="Valor cobrado por hora")
    daily_price: Optional[float] = Field(default=None, description="Valor cobrado por diária")
