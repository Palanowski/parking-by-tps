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
from datetime import datetime

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


def start_detector() -> subprocess.Popen:
    """Inicia o processo leitor (uma única vez). Reinicia se ele tiver morrido."""
    global _process
    if _process is not None and _process.poll() is None:
        return _process
    _process = subprocess.Popen(
        [sys.executable, "-m", "models.lpr"],
        cwd=PROJECT_ROOT,
    )
    log.info("Leitor de placas iniciado (pid %s)", _process.pid)
    return _process


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
