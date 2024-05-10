import logging

from server.config.frontend import ConfigFrontend
import os
from config.manager import ConfigManager
from config.manager import initialize_app_structure
from config.manager import data_folder
from config.manager import known_faces_folder
from config.manager import config_file
import json

# logging.basicConfig(level=logging.DEBUG)
default_config = initialize_app_structure()

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
    config_manager = ConfigManager(config_file)

    config_server = ConfigFrontend(config_manager)
    config_server.run()


if __name__ == '__main__':
    main()
