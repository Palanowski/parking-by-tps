"""Captura RTSP com baixa latência.

Uma thread consome o stream o tempo todo com `grab()` (só demux/decodificação,
sem converter cor) para o buffer nunca acumular atraso. A conversão para BGR
(`retrieve()`), que é a parte cara em resolução alta, só acontece quando o
leitor pede um quadro.
"""

import logging
import os
import threading
import time

import cv2
import numpy as np

from .config import redact

log = logging.getLogger("lpr.camera")

# Precisa estar no ambiente antes do primeiro VideoCapture com FFmpeg.
os.environ.setdefault(
    "OPENCV_FFMPEG_CAPTURE_OPTIONS",
    "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay|max_delay;500000",
)


def open_capture(url: str, timeout_ms: int = 5000) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(
        url,
        cv2.CAP_FFMPEG,
        [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout_ms,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, timeout_ms,
        ],
    )
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


class LatestFrameCamera:
    def __init__(self, url: str):
        self.url = url
        self._stop = threading.Event()
        self._want = threading.Event()
        self._ready = threading.Event()
        self._frame: np.ndarray | None = None
        self.connected = False
        self._thread = threading.Thread(target=self._loop, name="lpr-camera", daemon=True)

    def start(self) -> "LatestFrameCamera":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        self._want.set()
        self._thread.join(timeout=5)

    def read(self, timeout: float = 2.0) -> np.ndarray | None:
        """Retorna o quadro mais recente do stream, ou None se indisponível."""
        self._ready.clear()
        self._want.set()
        if not self._ready.wait(timeout):
            return None
        frame, self._frame = self._frame, None
        return frame

    def _loop(self) -> None:
        backoff = 1.0
        while not self._stop.is_set():
            cap = open_capture(self.url)
            if not cap.isOpened():
                log.warning("Não abriu %s; tentando de novo em %.0fs", redact(self.url), backoff)
                cap.release()
                self._stop.wait(backoff)
                backoff = min(backoff * 2, 30.0)
                continue

            log.info("Câmera conectada: %s", redact(self.url))
            self.connected = True
            backoff = 1.0
            failures = 0
            while not self._stop.is_set():
                if not cap.grab():
                    failures += 1
                    if failures >= 25:
                        log.warning("Stream parou de responder; reconectando")
                        break
                    time.sleep(0.02)
                    continue
                failures = 0
                if self._want.is_set():
                    ok, frame = cap.retrieve()
                    if ok:
                        self._frame = frame
                        self._want.clear()
                        self._ready.set()
            self.connected = False
            cap.release()
