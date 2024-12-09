from pydantic import BaseModel, Field


class ParkingModel(BaseModel):
    """Modelo para adicionar uma nova entrada de veículo."""

    plate: str = Field(..., description="Placa do veículo")
    barcode: str = Field(..., description="Código de barras")
    model: str = Field(..., description="Modelo do veículo")
    category: str = Field(..., description="Categoria do veículo")
    color: str = Field(..., description="Cor do veículo")
    status: str = Field(..., description="Status do veículo, EM ABERTO, CANCELADO, FINALIZADO")
    entry_user: str = Field(..., description="Usuário responsável pela entrada do veículo")
