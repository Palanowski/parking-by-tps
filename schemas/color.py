from pydantic import BaseModel, Field


class ColorModel(BaseModel):
    """Modelo para adicionar uma nova cor."""

    id: str = Field(..., description="Nome da cor")
