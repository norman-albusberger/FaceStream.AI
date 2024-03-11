# Erste Stufe: Builder-Image
FROM python:3.8-slim-buster AS builder

# Installieren der notwendigen Systempakete für die Kompilierung
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    gfortran \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Erstellen eines virtuellen Python-Umgebungsverzeichnisses
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Manuelle Installation von dlib
RUN pip install --upgrade pip && \
    git clone -b 'v19.21' --single-branch https://github.com/davisking/dlib.git && \
    cd dlib/ && \
    python3 setup.py install --set BUILD_SHARED_LIBS=OFF

# Installieren von face_recognition und anderen benötigten Paketen
RUN pip install face_recognition opencv-contrib-python-headless flask flask-requests

# Zweite Stufe: Runtime-Image
FROM python:3.8-slim-buster AS runtime

# Kopieren der virtuellen Umgebung vom Builder-Image
COPY --from=builder /opt/venv /opt/venv

# Setzen des Pfades für die virtuelle Umgebung
ENV PATH="/opt/venv/bin:$PATH"

# Installieren von Runtime-Abhängigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Anwendungsdateien in das Arbeitsverzeichnis kopieren
#COPY . /app


CMD ["python", "face-recognition-stream.py"]
