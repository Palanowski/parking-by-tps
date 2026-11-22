"""Configuração do leitor de placas, lida do arquivo .env do projeto.

Variáveis (todas opcionais, exceto a câmera):
    CAMERA_URL            URL RTSP completa. Se definida, ignora as quatro abaixo.
    CAMERA_IP             IP da câmera.
    CAMERA_USER           Usuário da câmera.
    CAMERA_PASS           Senha da câmera.
    CAMERA_RTSP_PATH      Caminho do stream (padrão: onvif1). Descubra com
                          `python -m models.lpr --probe`.
    LPR_ROI               Região de interesse "x1,y1,x2,y2" no quadro original.
                          Vazio = quadro inteiro.
    LPR_FPS               Quadros analisados por segundo (padrão: 4).
    LPR_MOTION_THRESHOLD  Fração de pixels alterados no ROI para considerar
                          movimento (padrão: 0.004).
    LPR_ACTIVE_SECONDS    Segundos que o leitor continua analisando após o
                          último movimento, p/ carro parado na cancela (padrão: 6).
    LPR_MIN_CONF          Confiança mínima média do OCR (padrão: 0.6).
    LPR_VOTES             Leituras iguais necessárias para confirmar (padrão: 2).
    LPR_VOTE_WINDOW       Janela em segundos para somar votos (padrão: 4).
    LPR_COOLDOWN          Segundos para ignorar a mesma placa depois de
                          confirmada (padrão: 120).
    LPR_DETECTOR_MODEL    Modelo detector do open-image-models.
    LPR_OCR_MODEL         Modelo OCR do fast-plate-ocr.
    LPR_THREADS           Threads do ONNX Runtime por modelo (padrão: 2).
"""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value else default


def _int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _roi(value: str | None) -> tuple[int, int, int, int] | None:
    if not value:
        return None
    parts = [int(p) for p in value.replace(" ", "").split(",")]
    if len(parts) != 4:
        raise ValueError(f"LPR_ROI inválido: {value!r} (esperado x1,y1,x2,y2)")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"LPR_ROI inválido: {value!r} (x2>x1 e y2>y1)")
    return x1, y1, x2, y2


def camera_host() -> str:
    ip = os.getenv("CAMERA_IP", "")
    user = os.getenv("CAMERA_USER", "")
    password = os.getenv("CAMERA_PASS", "")
    if user:
        return f"{quote(user, safe='')}:{quote(password, safe='')}@{ip}"
    return ip


def camera_url() -> str:
    url = os.getenv("CAMERA_URL")
    if url:
        return url
    if not os.getenv("CAMERA_IP"):
        raise RuntimeError("Defina CAMERA_URL ou CAMERA_IP no arquivo .env")
    path = os.getenv("CAMERA_RTSP_PATH", "onvif1").lstrip("/")
    return f"rtsp://{camera_host()}:554/{path}"


@dataclass(frozen=True)
class LprConfig:
    camera_url: str
    roi: tuple[int, int, int, int] | None
    fps: float
    motion_threshold: float
    active_seconds: float
    min_conf: float
    votes: int
    vote_window: float
    cooldown: float
    detector_model: str
    ocr_model: str
    threads: int

    @classmethod
    def from_env(cls) -> "LprConfig":
        return cls(
            camera_url=camera_url(),
            roi=_roi(os.getenv("LPR_ROI", "150,650,2540,1300")),
            fps=_float("LPR_FPS", 4.0),
            motion_threshold=_float("LPR_MOTION_THRESHOLD", 0.004),
            active_seconds=_float("LPR_ACTIVE_SECONDS", 6.0),
            min_conf=_float("LPR_MIN_CONF", 0.6),
            votes=_int("LPR_VOTES", 2),
            vote_window=_float("LPR_VOTE_WINDOW", 4.0),
            cooldown=_float("LPR_COOLDOWN", 120.0),
            detector_model=os.getenv("LPR_DETECTOR_MODEL", "yolo-v9-t-384-license-plate-end2end"),
            ocr_model=os.getenv("LPR_OCR_MODEL", "cct-xs-v2-global-model"),
            threads=_int("LPR_THREADS", 2),
        )


def redact(url: str) -> str:
    """Esconde a senha de uma URL RTSP para logar."""
    if "@" not in url or "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    creds, host = rest.rsplit("@", 1)
    user = creds.split(":", 1)[0]
    return f"{scheme}://{user}:***@{host}"
