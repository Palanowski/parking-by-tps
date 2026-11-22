"""Integração do leitor de placas com o sistema.

- `start_detector()` / `stop_detector()`: sobem e derrubam o processo leitor
  (`python -m models.lpr`), separado da interface Tk para não travá-la.
- `on_plate_detected()`: grava a saída do veículo no banco; é chamada dentro
  do processo leitor a cada placa confirmada.
"""

import atexit
import logging
import subprocess
import sys
import logging
from datetime import datetime
from parkocr import Detector
from models.parking import get_parking_by_plate, update_parking, calc_exit_status, insert_exit_plate_time
from schemas.parking import UpdateParkingModel

from models.lpr.config import PROJECT_ROOT

log = logging.getLogger("lpr.detector")

_process: subprocess.Popen | None = None


def on_plate_detected(plate: str) -> None:
    from models.parking import (
        calc_exit_status,
        get_parking_by_plate,
        insert_exit_plate_time,
        update_parking,
    )

    key = plate[3:]  # as 3 letras iniciais são desconsideradas de propósito
    now = datetime.now()
    parking = get_parking_by_plate(key)
    if not parking:
        insert_exit_plate_time(key, now.time(), "DIVERGENTE")
        log.info("Saída %s sem entrada registrada -> DIVERGENTE", plate)
        return

    status = "NORMAL"
    if parking["status"] in ("FINALIZADO", "DESISTENCIA"):
        delta_time = datetime.strptime(parking["delta_time"], "%H:%M:%S")
        status = calc_exit_status(delta_time, parking["entry_time"], now)
    elif parking["status"] in ("EM ABERTO", "RETORNO"):
        status = "DIVERGENTE"
    update_parking(key, exit_plate_time=now.time(), exit_status=status)
    log.info("Saída %s registrada -> %s", plate, status)


def on_plate_detected(plate: str):
    now = datetime.now()
    parking = get_parking_by_plate(plate[3:])
    if parking:
        if parking.status == "FINALIZADO":
            status = calc_exit_status(parking["delta_time"], parking["entry_time"], now)
        elif parking.status in ["EM ABERTO", "RETORNO"]:
            status = "DIVERGENTE"
        update_parking(plate[3:], UpdateParkingModel(
            exit_plate_time=now,
            exit_status=status
        ))
    else:
        insert_exit_plate_time(plate[3:], now, "DIVERGENTE")


def stop_detector() -> None:
    global _process
    if _process is None or _process.poll() is not None:
        return
    _process.terminate()
    try:
        _process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _process.kill()
    _process = None


def watch_detector(root, interval_ms: int = 30000) -> None:
    """Confere periodicamente pelo loop do Tk e reinicia o leitor se ele caiu."""
    if _process is not None and _process.poll() is not None:
        log.warning("Leitor de placas encerrou (código %s); reiniciando", _process.returncode)
        start_detector()
    root.after(interval_ms, watch_detector, root, interval_ms)


atexit.register(stop_detector)
