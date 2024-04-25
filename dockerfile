# Erste Stufe: Builder-Image
FROM python:3.8-slim-buster AS builder

# Installieren der notwendigen Systempakete und Build-Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-numpy \
    cmake \
    gfortran \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Erstellen eines virtuellen Python-Umgebungsverzeichnisses
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Dlib
ENV CFLAGS=-static
RUN pip3 install --upgrade pip && \
    git clone -b 'v19.21' --single-branch https://github.com/davisking/dlib.git && \
    cd dlib/ && \
    python3 setup.py install --set BUILD_SHARED_LIBS=OFF

# Installieren von face_recognition und anderen benötigten Paketen
RUN pip3 install face_recognition opencv-contrib-python-headless flask flask-requests requests psutil

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
    supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis festlegen
WORKDIR /FaceStream.ai

# Anwendungskode für beide Server kopieren
COPY app ./app

# Supervisor-Konfigurationsdatei kopieren
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ports exponieren
EXPOSE 5000
EXPOSE 5001

# Supervisor als Hauptprozess starten
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
