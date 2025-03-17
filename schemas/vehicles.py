from pydantic import BaseModel, Field


class VehicleModel(BaseModel):
    """Modelo para adicionar um novo modelo de veículo."""

    plate: str = Field(..., description="Placa do veículo")
    color: str = Field(..., description="Cor do veículo")
    category: str = Field(..., description="Categoria do veículo")
    model: str = Field(..., description="Modelo do veículo")
