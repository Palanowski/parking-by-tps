from datetime import time, timedelta
from typing import Optional
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


class UpdateParkingModel(BaseModel):
    """Modelo para adicionar uma nova entrada de veículo."""

    exit_time: Optional[time] = Field(default=None, description="Status do veículo, EM ABERTO, CANCELADO, FINALIZADO")
    delta_time: Optional[timedelta] = Field(default=None, description="Tempo total de permanência")
    status: Optional[str] = Field(default=None, description="Status do veículo, EM ABERTO, CANCELADO, FINALIZADO")
    exit_user: Optional[str] = Field(default=None, description="Usuário responsável pela saída do veículo")
    total_value: Optional[float] = Field(default=None, description="Valor total pago")
    ISreturn: Optional[bool] = Field(default=None, description="Flag para identificar veículos que retornaram")
    partialPayment: Optional[float] = Field(default=None, description="Valor parcial já pago")
    addition: Optional[float] = Field(default=None, description="Valor de acréscimo aplicado")
    discount: Optional[float] = Field(default=None, description="Valor de desconto aplicado")
