"""Processo leitor de placas.

Uso:
    python -m models.lpr            roda o leitor (é o que o main.py inicia)
    python -m models.lpr --probe    procura o caminho RTSP que a câmera aceita
    python -m models.lpr --image F  lê placas de uma imagem (teste, sem banco)
    python -m models.lpr --dry-run  roda na câmera só logando, sem gravar no banco
"""

import argparse
import logging
import os
import signal
import sys
import threading
import time

from .config import PROJECT_ROOT, LprConfig, redact

log = logging.getLogger("lpr")

PROBE_PATHS = [
    "onvif1", "onvif2", "live", "h264", "h264/ch1/main/av_stream",
    "cam/realmonitor?channel=1&subtype=0", "Streaming/Channels/101",
    "axis-media/media.amp", "live/ch00_0", "stream1", "11",
]


def probe() -> int:
    import cv2

    from .camera import open_capture
    from .config import camera_host

    host = camera_host()
    for path in PROBE_PATHS:
        url = f"rtsp://{host}:554/{path}"
        cap = open_capture(url, timeout_ms=3000)
        ok = cap.isOpened() and cap.read()[0]
        size = f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}" if ok else ""
        cap.release()
        print(f"{'OK ' if ok else '-- '} {redact(url)} {size}")
        if ok:
            print(f"\nColoque no .env:  CAMERA_RTSP_PATH={path}")
            return 0
    print("Nenhum caminho funcionou. Confira IP/usuário/senha ou informe CAMERA_URL.")
    return 1


def read_image(path: str) -> int:
    import cv2

    from .recognizer import PlateRecognizer

    from dataclasses import replace

    os.environ.setdefault("CAMERA_URL", "rtsp://offline")  # câmera não é usada aqui
    cfg = replace(LprConfig.from_env(), roi=None)
    image = cv2.imread(path)
    if image is None:
        print(f"Não abriu {path}")
        return 1
    rec = PlateRecognizer(cfg)
    rec.read(image)  # aquece
    t = time.perf_counter()
    plates = rec.read(image)
    ms = (time.perf_counter() - t) * 1000
    print(f"{path}: {plates or 'nenhuma placa'}  ({ms:.0f} ms)")
    return 0


def run(dry_run: bool = False) -> int:
    from .camera import LatestFrameCamera
    from .recognizer import PlateRecognizer

    if dry_run:
        def handle(plate: str) -> None:
            log.info("[dry-run] %s", plate)
    else:
        from models.detector import on_plate_detected as handle

    cfg = LprConfig.from_env()
    log.info("Carregando modelos (%s / %s)...", cfg.detector_model, cfg.ocr_model)
    recognizer = PlateRecognizer(cfg)
    camera = LatestFrameCamera(cfg.camera_url).start()

    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    parent = os.getppid()
    interval = 1.0 / cfg.fps
    log.info("Leitor iniciado: %s | ROI=%s | %.1f fps", redact(cfg.camera_url), cfg.roi, cfg.fps)

    try:
        while not stop.is_set():
            started = time.monotonic()
            if os.getppid() != parent:  # a interface fechou
                log.info("Processo pai encerrou; saindo")
                break
            frame = camera.read()
            if frame is not None:
                for plate in recognizer.process(frame):
                    try:
                        handle(plate)
                    except Exception:
                        log.exception("Erro ao registrar a placa %s", plate)
            stop.wait(max(0.0, interval - (time.monotonic() - started)))
    finally:
        camera.stop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m models.lpr")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--image")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    if args.probe:
        return probe()
    if args.image:
        return read_image(args.image)
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
