import json
import os


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
        """Konvertiert einen Hex-Farbwert in ein RGB-Tupel."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb_color):
        """Konvertiert ein RGB-Tupel in einen Hex-Farbwert."""
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

    def get_rgba_overlay(self):

        """Berechnet den RGBA-Wert für das Overlay basierend auf der Overlay-Farbe in der Konfiguration."""
        rgb_color = self.get('overlay_color', [220,220,200])  # Standardfarbe, falls keine angegeben ist
        alpha = 1-self.get('overlay_transparency', 0.5)
        rgba_color = 'rgba({}, {}, {}, {})'.format(*rgb_color, alpha)
        return rgba_color
