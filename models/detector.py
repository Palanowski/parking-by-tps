import cv2
import sys
import logging
from datetime import datetime
from parkocr import Detector
from models.parking import get_parking_by_plate, update_parking, calc_exit_status, insert_exit_plate_time
from schemas.parking import UpdateParkingModel

logging.basicConfig(level=logging.INFO, format="%(message)s")


CAMERA_IP = "192.168.1.2"     # find camera IP on your network
CAMERA_USER = "admin"
CAMERA_PASS = "Serenalui18"


COMMON_PATHS = [
    "rtsp://{ip}:554/onvif1",
    "rtsp://{ip}:554/onvif2",
    "rtsp://{ip}:554/onvif1?tcp",
    "rtsp://{ip}:554/onvif2?tcp",
    "rtsp://{ip}/live",
    "rtsp://{ip}/h264",
    "rtsp://{ip}/h264/ch1/main/av_stream",
    "rtsp://{ip}/cam/realmonitor?channel=1&subtype=0",
    "rtsp://{ip}/Streaming/Channels/101",
    "rtsp://{ip}/axis-media/media.amp",
    "rtsp://{ip}/live/ch00_0",
    "rtsp://{ip}/user=admin&password=&channel=1&stream=0.sdp",
]


def find_camera(ip: str, username: str = "", password: str = "") -> str | None:
    """
    Iterate over common RTSP endpoints and return the first working URL.
    Find your camera local IP and configure credentials first. If your
    camera model uses a different url pattern, add it to COMMON_PATHS.
    """
    for path in COMMON_PATHS:
        if username and password:
            url = path.format(ip=f"{username}:{password}@{ip}")
        else:
            url = path.format(ip=ip)
        logging.info(f"Trying: {url}")
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ok, _ = cap.read()
            cap.release()
            if ok:
                logging.info(f"Found working stream: {url}")
                return url
    logging.warning("No working stream found.")
    return None


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


if __name__ == "__main__":
    url = find_camera(CAMERA_IP, CAMERA_USER, CAMERA_PASS)
    if url:
        print("Camera stream URL:", url)
    else:
        print("No stream found.")
        sys.exit(1)
    det = Detector(
        rtsp_url=url,
        # roi=(500, 200, 1200, 600),
        headless=False,
        on_detect=on_plate_detected,
        fifo_output='/tmp/plate_fifo',
        screenshot="roi"
    )
    det.run()