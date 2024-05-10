import logging
import os
import queue
from server.streaming.video import VideoStreamingServer
from processor.frame import FrameProcessor
from loader.face import FaceLoader
from notification.service import NotificationService
from manager.camera import CameraManager
from config.manager import ConfigManager


# Aktiviere Logging für bessere Fehlerbehebung
# logging.basicConfig(level=logging.DEBUG)


def main():
    # Konfiguration laden
    config_path = os.path.join('/data', 'config.json')
    config_manager = ConfigManager(config_path)
    config_manager.load_config()

    # Warteschlange für frames
    frame_queue = queue.Queue(maxsize=100)
    processed_frame_queue = queue.Queue(maxsize=50)
    output_size = (config_manager.get('output_width'), config_manager.get('output_height'))
    # Starten des Kamera Managers
    camera_manager = CameraManager(frame_queue, config_manager.get('input_stream_url'), output_size)
    camera_manager.start()

    # NotificationService
    notification_service = NotificationService(config_manager)

    # Laden der bekannten Gesichter
    face_loader = FaceLoader()

    # Frame Processor
    frame_processor = FrameProcessor(frame_queue, processed_frame_queue, face_loader, config_manager,
                                     notification_service)
    frame_processor.start()

    server = VideoStreamingServer(config_manager, processed_frame_queue)
    server.run()


if __name__ == '__main__':
    main()
