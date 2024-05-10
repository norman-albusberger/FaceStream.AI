import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import re
from urllib.parse import urlparse
import logging
import json
from flask import send_file

UPLOAD_FOLDER = '/data/knownfaces'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_int(value, default, min_value=None, max_value=None):
    try:
        value = int(value)
        if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
            return default
        return value
    except (ValueError, TypeError):
        return default


def validate_bool(value, default):
    logging.debug(value)
    if str(value).lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    elif str(value).lower() in ['false', '0', 'f', 'n', 'no']:
        return False
    else:
        return default


# Funktion zur Validierung von Hex-Farben
def validate_hex_color(value, default):
    if value and re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
        return value
    else:
        return default


# Funktion zur Validierung von URLs
def validate_url(value, default):
    try:
        result = urlparse(value)
        if all([result.scheme, result.netloc]):
            return value
    except:
        pass
    return default


def validate_port(value, default=''):
    try:
        port = int(value)
        if 1 <= port <= 65535:
            return port
        else:
            raise ValueError("Port number out of range")
    except (ValueError, TypeError):
        logging.error(f"Invalid port number provided: {value}, reverting to default: {default}")
        return default


def validate_float(value, default, min_value=0.0, max_value=1.0):
    try:
        value = float(value)
        if value < min_value or value > max_value:
            return default
        return value
    except (TypeError, ValueError):
        return default


class ConfigFrontend:
    def __init__(self, config_manager):
        self.app = Flask(__name__)
        self.config_manager = config_manager
        self.define_routes()

    def define_routes(self):

        @self.app.route('/api/setBaseUrl', methods=['POST'])
        def set_base_url():
            data = request.get_json()
            base_url = data['baseUrl']
            # Setzen der Basis-URL im Konfigurationsmanager
            self.config_manager.set('base_url', base_url)
            self.config_manager.save_config()
            return jsonify({'status': 'URL set successfully', 'baseUrl': base_url})

        @self.app.route('/test_path')
        def test_path():
            try:
                files_list = os.listdir(UPLOAD_FOLDER)
                return jsonify({'files': files_list,
                                'uploadfolder': UPLOAD_FOLDER
                                }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            print(self.config_manager.config)
            hex_color = self.config_manager.rgb_to_hex(self.config_manager.get('overlay_color'))
            rgba_overlay = self.config_manager.get_rgba_overlay()
            transparency_value = int(round((self.config_manager.get('overlay_transparency')) * 100))
            faces = os.listdir(UPLOAD_FOLDER)
            if request.method == 'POST':
                new_config = {
                    'input_stream_url': validate_url(request.form.get('input_stream_url'), ''),
                    'overlay_color': self.config_manager.hex_to_rgb(request.form.get('overlay_color')),
                    'overlay_transparency': validate_int(request.form.get('overlay_transparency'), 0, 0, 100) / 100,
                    'overlay_border': validate_int(request.form.get('overlay_border'), 1, 1, 4),
                    'output_width': validate_int(request.form.get('output_width'), 640, 100, 4000),
                    'output_height': validate_int(request.form.get('output_height'), 480, 100, 4000),
                    'custom_message_udp': request.form.get('custom_message_udp',
                                                           '[[name]], spotted at [[time]] on [[date]]!').strip(),
                    'custom_message_http': request.form.get('custom_message_http',
                                                            '[[name]], spotted at [[time]] on [[date]]!').strip(),
                    'use_udp': validate_bool(request.form.get('use_udp'), False),
                    'use_web': validate_bool(
                        request.form.get('use_web'), False),
                    'web_service_url': request.form.get('web_service_url'),
                    'udp_service_url': request.form.get('udp_service_url'),
                    'udp_service_port': validate_port(request.form.get('udp_service_port')),
                    'notification_delay': validate_int(request.form.get('notification_delay'), 60, 10, max_value=300),
                    'face_recognition_interval': validate_int(request.form.get('face_recognition_interval'), 60, 2,
                                                              max_value=300)
                }
                combined = {**self.config_manager.config, **new_config}

                self.config_manager.config = combined
                self.config_manager.save_config()

                # Neustart des Video-Stream Servers erforderlich, um Änderungen anzuwenden
                with open('/data/signal_file', 'w') as f:
                    f.write("restart")

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

        @self.app.route('/delete_image/<filename>', methods=['POST'])
        def delete_image(filename):
            # Der vollständige Pfad zur Datei
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # Überprüfung, ob die Datei existiert
            if os.path.exists(file_path):
                # Versuchen, die Datei zu löschen
                try:
                    os.remove(file_path)
                    return redirect(url_for('index'))
                except Exception as e:
                    return jsonify({'error': f'Fehler beim Löschen von {filename}: {str(e)}'}), 500
            else:
                # Wenn die Datei nicht gefunden wurde
                return jsonify({'error': f'Bild {filename} nicht gefunden'}), 404

        @self.app.route('/event_log')
        def show_log():
            try:
                log_file = self.config_manager.get('log_file')

                # Öffnen der Datei und Erstellen eines JSON-Arrays
                with open(log_file, 'r') as file:
                    entries = [json.loads(line) for line in file if line.strip()]
                return jsonify(entries)  # Gibt ein valides JSON-Array zurück

            except Exception as e:
                # Im Fehlerfall geben wir eine Fehlermeldung und den HTTP-Statuscode 500 zurück
                return jsonify({'error': str(e)}), 500

        @self.app.route('/list-faces')
        def list_faces():
            faces = os.listdir(UPLOAD_FOLDER)
            print(faces)

            return render_template('_face_list.html', faces=faces)

        @self.app.route('/knownfaces/<filename>')
        def knownfaces(filename):
            # Simple security measure to prevent path traversal
            if '..' in filename or filename.startswith('/'):
                return "Access denied", 403

            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            uploadfolder = os.path.join(BASE_DIR, UPLOAD_FOLDER)
            return send_from_directory(uploadfolder, filename)

        @self.app.route('/event-image/<filename>')
        def event_image(filename):
            # Einfache Sicherheitsmaßnahme zur Verhinderung von Path Traversal
            if '..' in filename or filename.startswith('/'):
                return "Access denied", 403

            # Bestimmung des Basisverzeichnisses
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Holen des Pfades aus der Konfiguration
            image_path = os.path.join(base_dir, self.config_manager.get('image_path'))

            try:
                # Sicherstellen, dass der Pfad existiert und ein Verzeichnis ist
                if not os.path.exists(image_path) or not os.path.isdir(image_path):
                    raise FileNotFoundError("The specified image directory does not exist.")

                # Senden der Datei aus dem angegebenen Verzeichnis
                return send_from_directory(image_path, filename)
            except FileNotFoundError as e:
                # Fehlerbehandlung, falls der Pfad nicht existiert
                return str(e), 404

        @self.app.route('/last-event-image')
        def last_event_image():
            image_path = self.config_manager.get('image_path')
            # Alle Dateien im Verzeichnis auflisten
            files = [os.path.join(image_path, f) for f in os.listdir(image_path)]
            # Die neueste Datei finden basierend auf der Erstellungszeit
            latest_file = max(files, key=os.path.getctime)
            # Die neueste Datei senden
            return send_file(latest_file, mimetype='image/jpeg')  # Mimetype entsprechend anpassen

    def run(self):
        self.app.run(
            host='0.0.0.0',  # interner server jeder Adresse des hosts aus erreichbar
            port=5000,  # Einstellung für den Port des Konfigurationsservers
            threaded=True,
            use_reloader=False,
            debug=True
        )
