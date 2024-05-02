from server.config.frontend import ConfigFrontend
import os
from config.manager import ConfigManager
import json


def initialize_app_structure():
    data_folder = 'data'
    known_faces_folder = os.path.join(data_folder, 'knownfaces')
    config_file = os.path.join(data_folder, 'config.json')
    default_config = {
        # Hier Ihre Standardkonfigurationswerte einfügen
        'input_stream_url': '...',
        'overlay_color': [220, 220, 200],
        'overlay_transparency': 0.5,
        'overlay_border': 1,
        'output_width': 640,
        'output_height': 480,
        'enable_notification_service': False,
        'notification_service_address': '',
        'notification_service_port': None,
        'notification_period': 60,
        'face_recognition_interval': 60
    }

    # Erstellen des 'data'-Ordners, falls nicht vorhanden
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Erstellen des 'knownfaces'-Ordners, falls nicht vorhanden
    if not os.path.exists(known_faces_folder):
        os.makedirs(known_faces_folder)

    # Erstellen der 'config.json'-Datei mit Standardwerten, falls nicht vorhanden
    if not os.path.isfile(config_file):
        with open(config_file, 'w') as config_file_handle:
            json.dump(default_config, config_file_handle, indent=4)


def main():
    # Initialisieren der Anwendungsstruktur
    initialize_app_structure()
    config_path = os.path.join('data', 'config.json')
    config_manager = ConfigManager(config_path)

    config_server = ConfigFrontend(config_manager)
    config_server.run()


if __name__ == '__main__':
    main()
