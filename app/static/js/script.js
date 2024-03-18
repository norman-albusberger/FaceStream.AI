const colorPicker = document.getElementById('colorPicker');
const transparencySlider = document.getElementById('overlayTransparency');
const colorOverlay = document.getElementById('colorOverlay');


function updateOverlay() {
    const color = colorPicker.value;
    const transparency = transparencySlider.value / 100;
    colorOverlay.style.backgroundColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${1 - transparency})`;
}

colorPicker.addEventListener('input', updateOverlay);
transparencySlider.addEventListener('input', updateOverlay);



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



function toggleNotificationServiceSettings() {
    var checkBox = document.getElementById("enableNotificationService");
    var settingsDiv = document.getElementById("notificationServiceSettings");

    // Zeigt oder verbirgt die Notification Service Einstellungen basierend auf dem Checkbox-Status
    if (checkBox.checked == true){
        settingsDiv.style.display = "block";
    } else {
        settingsDiv.style.display = "none";
    }
}

function setSize(width, height) {
    document.getElementById('outputWidth').value = width;
    document.getElementById('outputHeight').value = height;
}

function updateFaceRecognitionIntervalValue(value) {
              document.getElementById('faceRecognitionIntervalValue').innerHTML = value;
            }

// Sorgt dafür, dass die Einstellungen sichtbar bleiben, wenn die Seite neu geladen wird und die Checkbox aktiviert ist
document.addEventListener("DOMContentLoaded", function() {
    toggleNotificationServiceSettings();

     // Funktion zur Validierung der Formulardaten
    function validateForm() {
        var isEnabled = document.getElementById("enableNotificationService").checked;
        if (isEnabled) {
            var address = document.getElementById("notificationServiceAddress").value;
            var port = document.getElementById("notificationServicePort").value;
            var period = document.getElementById("notificationPeriod").value;

            if (!address) {
                alert("Bitte gib eine gültige Adresse ein.");
                return false;
            }
            if (!port || port < 1 || port > 65535) {
                alert("Bitte gib einen gültigen Port zwischen 1 und 65535 ein.");
                return false;
            }
            if (!period || period < 1) {
                alert("Bitte gib eine gültige Benachrichtigungsperiode ein.");
                return false;
            }
        }
        return true; // Alles ist valide
    }

    // Validierung beim Absenden des Formulars hinzufügen
    var form = document.querySelector("form"); // Annahme, dass es ein umgebendes <form>-Element gibt
    form.onsubmit = validateForm;


});