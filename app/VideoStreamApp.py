import os
from flask import Flask, Response, render_template, request, redirect, url_for
import cv2
import face_recognition
import time
from threading import Thread
import subprocess

from config.manager import ConfigManager
from loader.face import FaceLoader
from stream.video import VideoStream


def restart_server():
    """Führt einen verzögerten Neustart der Anwendung durch."""
    time.sleep(5)  # Wartezeit, um dem Benutzer Zeit zu geben, die Bestätigungsnachricht zu lesen
    subprocess.run(["touch", "/pfad/zum/verzeichnis/app.wsgi"])


class VideoStreamApp:
    def __init__(self, config_manager):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.video_stream = VideoStream(
            input_stream_url=config_manager.get('input_stream_url'),
            overlay_transparency=config_manager.get('overlay_transparency', 0.5),
            output_width=config_manager.get('output_width'),
            output_height=config_manager.get('output_height'),
            face_loader=FaceLoader()

        )
        self.define_routes()

    def define_routes(self):
        @self.app.route(self.config_manager.get('output_path'))
        def video_feed():
            return Response(self.video_stream.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/guide')
        def guide():
            return render_template('guide.html', stream_url=self.config_manager.get('input_stream_url'),
                                   host_ip=self.config_manager.get('output_host'),
                                   port=self.config_manager.get('output_port'),
                                   video_path=self.config_manager.get('output_path'))

        @self.app.route('/', methods=['GET', 'POST'])
        def config():
            config_manager = ConfigManager(os.path.join('data', 'config.json'))
            config_manager.load_config()
            actual_config = config_manager.config
            if request.method == 'POST':
                # Daten aus dem Formular übernehmen
                new_config = {
                    'input_stream_url': request.form.get('input_stream_url'),
                    'output_host': request.form.get('output_host'),
                    'output_port': int(request.form.get('output_port')),  # Umwandlung in Integer
                    'output_path': request.form.get('output_path'),
                    'image_directory': request.form.get('image_directory'),
                    'notification_service_url': request.form.get('notification_service_url'),
                    'overlay_transparency': float(request.form.get('overlay_transparency')),  # Umwandlung in Float
                    'output_width': int(request.form.get('output_width')),  # Umwandlung in Integer
                    'output_height': int(request.form.get('output_height'))  # Umwandlung in Integer
                }
                # Konfigurationsdatei aktualisieren
                config_manager.config = new_config
                config_manager.save_config()

                # Neustart in einem separaten Thread initiieren, um den aktuellen Request zu beenden
                from threading import Thread
                Thread(target=restart_server).start()

                # Benutzer auf die Startseite umleiten mit einer Verzögerung (JavaScript)
                return render_template('config_saved.html')

            else:
                actual_config = config_manager.config

            return render_template('config_form.html', config=actual_config)

    def run(self):
        self.app.run(
            host=self.config_manager.get('output_host'),
            port=self.config_manager.get('output_port'),
            threaded=True,
            use_reloader=False
        )


def main() -> object:
    # Konfigurationsmanager instanziieren
    config_path = os.path.join('data', 'config.json')
    config_manager = ConfigManager(config_path)

    # VideoStreamApp mit Konfigurationsmanager instanziieren
    video_stream_app = VideoStreamApp(config_manager)

    # Server starten
    video_stream_app.run()


if __name__ == '__main__':
    print(__name__)
    main()
