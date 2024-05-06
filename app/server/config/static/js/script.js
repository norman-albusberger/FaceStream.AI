const colorPicker = document.getElementById('colorPicker');
const transparencySlider = document.getElementById('overlayTransparency');
const colorOverlay = document.getElementById('colorOverlay');
var table = new Tabulator("#eventlog-table", {
    height: '600px',
    layout: 'fitColumns',
    columns: [
        {title: "Name", field: "name", sorter: "string", width: 200},
        {title: "Time", field: "timestamp", sorter: "timestamp"},
        {title: "Image Path", field: "image_path"},

    ],

});

function sendBaseUrlToServer() {
    const baseUrl = window.location.origin;
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({baseUrl})
    };

    fetch('/api/setBaseUrl', requestOptions)
        .then(response => response.json())
        .then(data => console.log('Response:', data))
        .catch(error => console.error('Error:', error));
}


function updateOverlay() {
    const color = colorPicker.value;
    const transparency = transparencySlider.value / 100;
    colorOverlay.style.backgroundColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${1 - transparency})`;
}

colorPicker.addEventListener('input', updateOverlay);
transparencySlider.addEventListener('input', updateOverlay);

function updateFacesList() {
    fetch('/list-faces')
        .then(response => response.text())  // Die Antwort als Text verarbeiten
        .then(html => {
            // Ersetzen Sie den Inhalt der Gesichterliste mit dem neuen HTML
            document.querySelector('.known-faces-list').innerHTML = html;
        })
        .catch(error => {
            console.error('Fehler beim Aktualisieren der Gesichterliste:', error);
        });
}

function updateDelayDisplay(value) {
    const minutes = Math.floor(value / 60);
    const seconds = value % 60;
    document.getElementById('notificationDelay').innerText = minutes > 0 ? `${minutes} minute(s) ${seconds} second(s)` : `${value} second(s)`;
}

function setSize(width, height) {
    document.getElementById('outputWidth').value = width;
    document.getElementById('outputHeight').value = height;
}

function updateFaceRecognitionIntervalValue(value) {
    document.getElementById('faceRecognitionIntervalValue').innerHTML = value;
}

document.addEventListener("DOMContentLoaded", function () {

    sendBaseUrlToServer();
    table.setData('/event_log');
    table.on("rowSelectionChanged", function(data, rows){
    document.getElementById("select-stats").innerHTML = data.length;
});

//form submit
    document.getElementById('submitFormButton').addEventListener('click', async function (event) {
        event.preventDefault(); // Verhindere das normale Abschicken des Formulars
        let self = this;

        let settingsForm = document.getElementById('settings-form');
        let notificationForm = document.getElementById('notification-form');

        if (!settingsForm.checkValidity() || !notificationForm.checkValidity()) {
            settingsForm.classList.add('was-validated');
            notificationForm.classList.add('was-validated');
            return; // Stoppe die Ausführung, wenn die Formulare ungültig sind
        }

        let formData = new FormData(settingsForm);
        new FormData(notificationForm).forEach((value, key) => formData.append(key, value));

        this.disabled = true; // Deaktiviere den Button
        this.classList.add('disabled');

        try {
            let response = await fetch(settingsForm.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Zeige das Modal an
                let modal = new bootstrap.Modal(document.getElementById('successModal'));
                modal.show();

                // Starte den Countdown
                let countdownElement = document.getElementById('countdown');
                let timeLeft = 20; // Zeit in Sekunden

                let timerId = setInterval(() => {
                    timeLeft--;
                    countdownElement.textContent = timeLeft;
                    if (timeLeft <= 0) {
                        clearInterval(timerId);
                        window.location.reload(); // Seite neu laden
                    }
                }, 1000);
            } else {
                throw new Error('Server antwortete mit einem Fehler: ' + response.status);
            }
        } catch (error) {
            console.error('Fehler beim Senden der Formulardaten', error);
            alert('Ein Fehler ist aufgetreten: ' + error.message);
        } finally {
            setTimeout(() => {
                self.disabled = false;
                self.classList.remove('disabled');
            }, 2000); // Wieder aktivieren nach 2 Sekunden
        }
    });


    document.getElementById('overlayTransparency').oninput = function () {
        document.getElementById('transparencyValue').innerText = this.value + '%';
    };

// Dropzone-Konfiguration
    Dropzone.options.knownFacesDropzone = {
        acceptedFiles: "image/jpeg,image/png,image/jpg",
        maxFilesize: 12, // Max. Dateigröße in MB
        dictInvalidFileType: "Ungültiges Dateiformat. Nur JPEG und PNG sind erlaubt.",

        success: function (file, response) {
            // Aktualisieren Sie die Liste der Gesichter
            updateFacesList();
        }
    }
});