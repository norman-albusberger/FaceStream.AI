# config_server.py
UPLOAD_FOLDER = '/data/knownfaces'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from config.manager import ConfigManager
from werkzeug.utils import secure_filename
import requests


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ConfigServer:
    def __init__(self, config_manager):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.define_routes()

    def define_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def config():
            hex_color = self.config_manager.rgb_to_hex(self.config_manager.get('overlay_color'))
            transparency_value = self.config_manager.get('overlay_transparency') * 100
            rgba_overlay = self.config_manager.get_rgba_overlay()
            overlay_transparency = float(request.form.get('overlay_transparency', 0)) / 100
            faces = os.listdir(UPLOAD_FOLDER)
            if request.method == 'POST':
                new_config = {
                    'input_stream_url': request.form.get('input_stream_url'),
                    'notification_service_url': request.form.get('notification_service_url'),
                    'overlay_transparency': overlay_transparency,
                    'overlay_color': self.config_manager.hex_to_rgb(request.form.get('overlay_color')),
                    'output_width': int(request.form.get('output_width')),
                    'output_height': int(request.form.get('output_height')),
                }
                self.config_manager.config = new_config
                self.config_manager.save_config()

                # Neustart des Video-Stream Servers erforderlich, um Änderungen anzuwenden

                return render_template('config_saved.html')
            else:
                return render_template(
                    'config_form.html',
                    config=self.config_manager.config,
                    hex_color=hex_color,
                    transparency_value=transparency_value,
                    rgba_overlay=rgba_overlay,
                    known_faces=faces
                )

        @self.app.route('/upload_faces', methods=['POST'])
        def upload_faces():
            # Überprüfung, ob 'file' Teil der Anfrage ist
            if 'file' not in request.files:
                return jsonify({'error': 'Keine Datei im Request gefunden'}), 400

            file = request.files['file']

            # Überprüfung, ob ein Dateiname vorhanden ist
            if file.filename == '':
                return jsonify({'error': 'Kein Dateiname angegeben'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                return jsonify({'message': f'Datei {filename} erfolgreich hochgeladen'}), 200

            # Standard-Antwort, falls die Datei nicht den Anforderungen entspricht
            return jsonify({'error': 'Ungültiges Dateiformat'}), 400

        @self.app.route('/list-faces')
        def list_faces():
            faces = os.listdir(UPLOAD_FOLDER)
            return render_template('_face_list.html', faces=faces)

        @self.app.route('/knownfaces/<filename>')
        def knownfaces(filename):
            return send_from_directory(UPLOAD_FOLDER, filename)

        @self.app.route('/trigger-restart')
        def trigger_restart():
            self.restart_video_stream_server()

    def run(self):
        self.app.run(
            host='0.0.0.0',  # Neue Einstellung für den Host des Konfigurationsservers
            port=5000,  # Neue Einstellung für den Port des Konfigurationsservers
            threaded=True,
            use_reloader=False
        )


def main():
    config_path = os.path.join('/data', 'config.json')
    config_manager = ConfigManager(config_path)

    config_server = ConfigServer(config_manager)
    config_server.run()


if __name__ == '__main__':
    main()
