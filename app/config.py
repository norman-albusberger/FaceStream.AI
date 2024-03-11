import os

# Konfiguration aus Umgebungsvariablen
INPUT_STREAM_URL = os.getenv('INPUT_STREAM_URL', '/dev/video0')
OUTPUT_HOST = os.getenv('OUTPUT_HOST', '0.0.0.0')
OUTPUT_PORT = int(os.getenv('OUTPUT_PORT', '5000'))
OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/video')
IMAGE_DIRECTORY = os.getenv('IMAGE_DIRECTORY', '/default/path/if/not/set')
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL')
OVERLAY_TRANSPARENCY = os.getenv('OVERLAY_TRANSPARENCY')

print(INPUT_STREAM_URL)
