import json
import os


class ConfigManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as json_file:
                self.config = json.load(json_file)


    def save_config(self):
        with open(self.filepath, 'w') as json_file:
            json.dump(self.config, json_file, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()
