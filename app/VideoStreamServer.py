# VideoStreamServer.py

import os
from flask import Flask, Response
from config.manager import ConfigManager
from stream.video import VideoStream
import threading
import time
import signal

from loader.face import FaceLoader


def check_for_restart_signal(signal_file_path, interval=10):
    while True:
        if os.path.exists(signal_file_path):
            print("Signaldatei gefunden. Server wird neu gestartet...")
            os.remove(signal_file_path)  # Signaldatei löschen
            os.kill(os.getpid(), signal.SIGTERM)  # Supervisord zum Neustart veranlassen
        time.sleep(interval)  # Wartezeit bis zur nächsten Überprüfung


class VideoStreamServer:
    def __init__(self, config_manager):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.video_stream = VideoStream(
            input_stream_url=self.config_manager.get('input_stream_url'),
            overlay_color=config_manager.get('overlay_color', [220, 220, 200]),
            overlay_transparency=self.config_manager.get('overlay_transparency', 0.5),
            output_width=self.config_manager.get('output_width'),
            output_height=self.config_manager.get('output_height'),
            face_loader=FaceLoader()
        )
        self.define_routes()

        signal_file_path = 'data/signal_file'  # Pfad zur Signaldatei für neustart
        restart_thread = threading.Thread(target=check_for_restart_signal, args=(signal_file_path,))
        restart_thread.daemon = True  # Stellen Sie sicher, dass der Thread als Daemon läuft
        restart_thread.start()

    def define_routes(self):
        @self.app.route('/')
        def video_feed():
            return Response(self.video_stream.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self):
        self.app.run(
            host='0.0.0.0',
            port=5001,  # Geändert zu 'video_stream_port'
            threaded=True,
            use_reloader=False
        )


def main():
    config_path = os.path.join('data', 'config.json')
    config_manager = ConfigManager(config_path)

    video_stream_server = VideoStreamServer(config_manager)
    video_stream_server.run()


if __name__ == '__main__':
    main()
