importScripts("/static/js/qr-scanner.min.js");

onmessage = function (e) {
  const imageData = e.data.imageData;
  const code = QrScanner.scanImage(imageData)
    .then((result) => {
      postMessage(result);
    })
    .catch((error) => {
      postMessage(null);
    });
};
