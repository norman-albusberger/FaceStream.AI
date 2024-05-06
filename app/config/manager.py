import json
import os

data_folder = '/data'
known_faces_folder = os.path.join(data_folder, 'knownfaces')
config_file = os.path.join(data_folder, 'config.json')


def initialize_app_structure():
    default_config = {
        'input_stream_url': '',
        'overlay_color': [220, 220, 200],
        'overlay_transparency': 0.5,
        'overlay_border': 1,
        'output_width': 640,
        'output_height': 480,
        'notification_delay': 60,  # Zeit in Sekunden
        'custom_message': {
            'name': '[[name]]',
            'image_url': '[[image_url]]',
            'time': '[[time]]',
            'date': '[[date]]',
        },
        'use_udp': False,
        'use_web': False,
        'web_service_url': '',
        'udp_service_port': 0,
        'udp_service_url': '',
        'face_recognition_interval': 60,
        'image_path': os.path.join('/data', 'saved_faces'),
        'log_file': os.path.join('/data', 'event_log.json')
    }
    return default_config


class ConfigManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Die Konfigurationsdatei {self.filepath} wurde nicht gefunden.")
        try:
            with open(self.filepath, 'r') as json_file:
                self.config = json.load(json_file)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Fehler beim Lesen der Konfigurationsdatei {self.filepath}: {e.msg}")

    def save_config(self):
        try:
            with open(self.filepath, 'w') as json_file:
                json.dump(self.config, json_file, indent=4)
        except Exception as e:
            raise IOError(f"Fehler beim Speichern der Konfigurationsdatei '{self.filepath}': {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def hex_to_rgb(self, hex_color):
        """Converts a Hex color value to an RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:  # Handles shorthand like #FFF
            hex_color = ''.join([c * 2 for c in hex_color])
        try:
            return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        except ValueError:
            raise ValueError("Invalid hex color format")

    def rgb_to_hex(self, rgb_color):
        """Konvertiert ein RGB-Tupel in einen Hex-Farbwert."""
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    def get_rgba_overlay(self):
        """Calculates the RGBA value for the overlay based on the overlay color in the configuration."""
        try:
            rgb_color = self.get('overlay_color', [220, 220, 200])  # Default color if none specified
            alpha = 1 - self.get('overlay_transparency', 0.5)
            rgba_color = 'rgba({}, {}, {}, {})'.format(*rgb_color, alpha)
            return rgba_color
        except Exception as e:
            raise ValueError("Error calculating RGBA overlay: {}".format(e))
