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