# VideoStreamServer.py

import os
from flask import Flask, Response
from config.manager import ConfigManager
from stream.video import VideoStream
import sys
import psutil
import logging

from loader.face import FaceLoader


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

    def define_routes(self):
        @self.app.route('/')
        def video_feed():
            return Response(self.video_stream.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/restart', methods=['POST'])
        def restart_server():

            """Restarts the current program, with file objects and descriptors
               cleanup
            """
            try:
                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logging.error(e)

            python = sys.executable
            os.execl(python, python, *sys.argv)

            return "Server wird neu gestartet", 200

    def run(self):
        self.app.run(
            host='0.0.0.0',
            port=5000,  # Geändert zu 'video_stream_port'
            threaded=True,
            use_reloader=False
        )


def main():
    config_path = os.path.join('/data', 'config.json')
    config_manager = ConfigManager(config_path)

    video_stream_server = VideoStreamServer(config_manager)
    video_stream_server.run()


if __name__ == '__main__':
    main()
