import cv2
import threading
import logging
from queue import Full


class CameraManager(threading.Thread):
    def __init__(self, frame_queue, camera_url, output_size=(640, 480)):
        super().__init__()
        self.camera_url = camera_url
        self.output_size = output_size
        self.frame_queue = frame_queue
        self.capture = None
        self.running = True

    def open_camera(self):
        self.capture = cv2.VideoCapture(self.camera_url)
        if not self.capture.isOpened():
            raise ValueError("Kamera konnte nicht geöffnet werden")

    def run(self):
        self.open_camera()
        while self.running:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    resized_frame = cv2.resize(frame, self.output_size)
                    try:
                        self.frame_queue.put(resized_frame,
                                             timeout=0.5)
                    except Full:
                        logging.error("Frame queue ist voll. Ältere Frames werden verworfen.")
                else:
                    logging.warning("Warnung: Kamera konnte kein Frame erfassen")
            else:
                logging.error("Kamera ist nicht geöffnet. Versuch, die Kamera neu zu öffnen")
                self.open_camera()

    def stop(self):
        self.running = False
        if self.capture and self.capture.isOpened():
            self.capture.release()
        logging.info("CameraManager gestoppt und Ressourcen freigegeben.")

    def close_camera(self):
        if self.capture:
            self.capture.release()

    def set_output_size(self, width, height):
        self.output_size = (width, height)
