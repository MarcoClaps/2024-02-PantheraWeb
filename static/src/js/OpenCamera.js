let camera_start = false;

function adattaZoom() {
    // Calcola l'altezza della finestra del browser
    var finestraAltezza = window.innerHeight;

    // Calcola l'altezza del contenuto della pagina
    var contenutoAltezza = document.documentElement.scrollHeight;

    // Calcola il fattore di scala
    var fattoreScala = finestraAltezza / contenutoAltezza;


    // Imposta il fattore di scala come zoom della pagina
    document.body.style.zoom = fattoreScala;
    const modal_content = document.getElementById("modal-content")
    modal_content.style.zoom = 200 - fattoreScala*100 + "%" ;
    if (fattoreScala >= 1) {
        modal_content.style.top = '30%';
    }
}

// Chiamata iniziale alla funzione per adattare lo zoom all'avvio
window.onload = adattaZoom;

// Aggiungi un gestore di eventi per adattare lo zoom anche quando la finestra viene ridimensionata
window.addEventListener("resize", adattaZoom);

function startCamera() {
    camera_start = true;
    navigator.mediaDevices.getUserMedia({video: true}).then(gotMedia).catch(error =>
        console.error('getUserMedia() error:', error));
    const vid = document.getElementById('videoElement');
    vid.style.display = 'block';
    // const scatta = document.getElementById('scatta');
    // scatta.style.display = 'block';
    const startcamera = document.getElementById('startcamera');
    startcamera.style.display = 'none';
    console.log("Camera started")
}

function gotMedia(mediaStream) {
    console.log("Got media");
    const videoElement = document.getElementById('videoElement');
    videoElement.srcObject = mediaStream;
    videoElement.addEventListener('loadedmetadata', function () {
        videoElement.play();
    });
}

function capture() {
    if (!camera_start) {
        console.log("Camera not started");
        startCamera();
        return;
    }
    console.log("Capture");
    const canvasElement = document.createElement('canvas');
    const context = canvasElement.getContext('2d');
    canvasElement.width = videoElement.videoWidth;
    canvasElement.height = videoElement.videoHeight;
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    const imageData = canvasElement.toDataURL('image/png');

    const img = document.getElementById("camera");
    // Pause the video and display the current frame as an image
    // #videoElement.pause();

    videoElement.style.display = 'none';
    img.style.display = 'block';
    img.src = imageData;

    // Generate a unique filename for the image (you can use a timestamp or a random string)
    const uniqueFilename = generateUniqueFilename();

    // Leggi la stringa di codifica in base64 come un blob e avvia la lettura del file
    const blob = new b64toBlob(imageData);
    const file = new File([blob], uniqueFilename, {type: "image/png"});
    const fd = new FormData();
    const modal = document.getElementById('modal');
    const loader = document.getElementById('loader');
    const result_enter = document.getElementById('result-enter');
    const result_error = document.getElementById('result-error');
    const modalText = document.getElementById('modal-text');
    modal.style.display = 'block';
    loader.style.display = 'block';
    modalText.style.display = 'block';
    modalText.textContent = 'Riconoscimento in corso...';
    modalText.style.backgroundColor = "blue";
    fd.append('file', file);

    $.ajax({
        type: 'POST',
        url: '/upload',
        data: fd,
        processData: false,
        contentType: false
    }).done(function (data) {
        $('#modal-text').text(data);
        console.log(data);
        // if the data starts with "Benvenuto" then the background color is green, otherwise it is red
        loader.style.display = 'none';
        if (data.startsWith("Benvenuto")) {
            result_enter.style.display = 'block';
            modalText.style.backgroundColor = "green";
        } else {
            result_error.style.display = 'block';
            modalText.style.backgroundColor = "red";
            modalText.textContent = data;
        }
        setTimeout(function () {
            window.location.reload();
        }, 10000);
    });
}

// Converti una stringa di codifica in base64 in un oggetto Blob
function b64toBlob(dataURI) {
    const byteString = atob(dataURI.split(',')[1]);
    const mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {type: mimeString});
}

// Function to generate a unique filename (you can use a timestamp or a random string)
function generateUniqueFilename() {
    // Implement your logic here to generate a unique filename
    // For example, you can use a timestamp or a random string
    // Example using a timestamp:
    return `${Date.now()}.png`;
}


function openCamera() {

    navigator.mediaDevices.getUserMedia({video: true}).then(gotMedia).catch(error =>
        console.error('getUserMedia() error:', error));

    function gotMedia(mediaStream) {
        const videoElement = document.createElement('video');
        videoElement.srcObject = mediaStream;

        videoElement.addEventListener('loadedmetadata', function () {
            videoElement.play();

            const canvasElement = document.createElement('canvas');
            const context = canvasElement.getContext('2d');
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;

            function capture() {
                context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
                const imageData = canvasElement.toDataURL('image/png');

                let img = document.getElementById("camera");
                img.src = imageData;

                const fd = new FormData();
                fd.append('file', b64toBlob(imageData), 'screenshot.png');

                $.ajax({
                    type: 'POST',
                    url: '/upload',
                    data: fd,
                    processData: false,
                    contentType: false
                }).done(function (data) {
                    $('#result').text(data);
                    console.log(data);
                });

                // window.setTimeout(capture, 100000);
            }

            capture();
        });
    }
}
