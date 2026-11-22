"""Detecção + OCR de placas, com filtro de movimento e votação entre quadros."""

import logging
import re
import statistics
import time
from collections import deque

import cv2
import numpy as np

from .config import LprConfig

log = logging.getLogger("lpr.recognizer")

# Antigo (ABC1234) e Mercosul (ABC1D23): LLL N (L|N) NN
PLATE_RE = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$")
_TO_LETTER = str.maketrans("01245678", "OIZASGTB")
_TO_DIGIT = str.maketrans("OQDIUZSBGTA", "00011258674")


def normalize_plate(text: str) -> str | None:
    """Corrige confusões comuns do OCR conforme a posição e valida o formato BR."""
    clean = re.sub(r"[^A-Z0-9]", "", (text or "").upper())
    if len(clean) != 7:
        return None
    fixed = (
        clean[:3].translate(_TO_LETTER)
        + clean[3].translate(_TO_DIGIT)
        + clean[4]
        + clean[5:].translate(_TO_DIGIT)
    )
    return fixed if PLATE_RE.match(fixed) else None


def _mean_conf(conf: float | list[float]) -> float:
    if isinstance(conf, (list, tuple, np.ndarray)):
        return float(statistics.fmean(conf)) if len(conf) else 0.0
    return float(conf)


class MotionGate:
    """Indica se houve movimento recente no ROI (barato: 320px, cinza)."""

    def __init__(self, threshold: float, active_seconds: float):
        self.threshold = threshold
        self.active_seconds = active_seconds
        self._prev: np.ndarray | None = None
        self._last_motion = 0.0

    def active(self, crop: np.ndarray, now: float) -> bool:
        h, w = crop.shape[:2]
        scale = 320 / w
        small = cv2.resize(crop, (320, max(1, int(h * scale))), interpolation=cv2.INTER_AREA)
        gray = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        if self._prev is not None and self._prev.shape == gray.shape:
            diff = cv2.absdiff(gray, self._prev)
            changed = np.count_nonzero(diff > 25) / diff.size
            if changed >= self.threshold:
                self._last_motion = now
        else:
            self._last_motion = now
        self._prev = gray
        return (now - self._last_motion) <= self.active_seconds


class PlateVoter:
    """Confirma uma placa após N leituras iguais numa janela, com cooldown."""

    def __init__(self, votes: int, window: float, cooldown: float):
        self.votes = votes
        self.window = window
        self.cooldown = cooldown
        self._reads: deque[tuple[float, str]] = deque()
        self._emitted: dict[str, float] = {}

    def add(self, plate: str, now: float) -> bool:
        while self._reads and now - self._reads[0][0] > self.window:
            self._reads.popleft()
        self._reads.append((now, plate))
        for p, t in list(self._emitted.items()):
            if now - t > self.cooldown:
                del self._emitted[p]
        if plate in self._emitted:
            return False
        if sum(1 for _, p in self._reads if p == plate) >= self.votes:
            self._emitted[plate] = now
            return True
        return False


class PlateRecognizer:
    def __init__(self, cfg: LprConfig):
        import onnxruntime as ort
        from fast_alpr import ALPR

        ort.set_default_logger_severity(3)
        providers = ["CPUExecutionProvider"]
        self.cfg = cfg
        self.alpr = ALPR(
            detector_model=cfg.detector_model,
            detector_conf_thresh=0.4,
            detector_providers=providers,
            detector_sess_options=_session_options(cfg.threads),
            ocr_model=cfg.ocr_model,
            ocr_providers=providers,
            ocr_sess_options=_session_options(cfg.threads),
        )
        self.motion = MotionGate(cfg.motion_threshold, cfg.active_seconds)
        self.voter = PlateVoter(cfg.votes, cfg.vote_window, cfg.cooldown)

    def crop(self, frame: np.ndarray) -> np.ndarray:
        if self.cfg.roi is None:
            return frame
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = self.cfg.roi
        return frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]

    def read(self, image: np.ndarray) -> list[tuple[str, float]]:
        """Lê todas as placas válidas da imagem: [(placa, confiança)]."""
        found = []
        for result in self.alpr.predict(image):
            if result.ocr is None:
                continue
            plate = normalize_plate(result.ocr.text)
            conf = _mean_conf(result.ocr.confidence)
            if plate and conf >= self.cfg.min_conf:
                found.append((plate, conf))
            elif result.ocr.text:
                log.debug("Descartada: %r conf=%.2f", result.ocr.text, conf)
        return found

    def process(self, frame: np.ndarray, now: float | None = None) -> list[str]:
        """Processa um quadro e devolve as placas confirmadas neste quadro."""
        now = time.monotonic() if now is None else now
        crop = self.crop(frame)
        if crop.size == 0 or not self.motion.active(crop, now):
            return []
        confirmed = []
        for plate, conf in self.read(crop):
            log.debug("Leitura: %s (%.2f)", plate, conf)
            if self.voter.add(plate, now):
                log.info("Placa confirmada: %s (conf %.2f)", plate, conf)
                confirmed.append(plate)
        return confirmed


def _session_options(threads: int):
    """Limita as threads do ONNX para não tomar todos os núcleos da máquina,
    que também roda a interface."""
    import onnxruntime as ort

    opts = ort.SessionOptions()
    opts.intra_op_num_threads = threads
    opts.inter_op_num_threads = 1
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    return opts
