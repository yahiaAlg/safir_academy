class QRScanner {
  constructor() {
    this.video = document.getElementById("scanner-video");
    this.toggleButton = document.getElementById("toggle-camera");
    this.switchButton = document.getElementById("switch-camera");
    this.errorMessage = document.getElementById("error-message");
    this.stream = null;
    this.scanning = false;
    this.canvas = document.createElement("canvas");
    this.canvasContext = this.canvas.getContext("2d");
    this.deviceIndex = 0;
    this.devices = [];

    this.toggleButton.addEventListener("click", () => this.toggleCamera());
    this.switchButton.addEventListener("click", () => this.switchCamera());
  }

  async init() {
    try {
      this.devices = await navigator.mediaDevices.enumerateDevices();
      this.devices = this.devices.filter(
        (device) => device.kind === "videoinput"
      );

      if (this.devices.length > 1) {
        this.switchButton.style.display = "inline-block";
      }
    } catch (error) {
      this.showError("Failed to enumerate devices: " + error.message);
    }
  }

  async toggleCamera() {
    if (this.stream) {
      this.stopCamera();
      this.toggleButton.textContent = "Start Camera";
    } else {
      await this.startCamera();
      this.toggleButton.textContent = "Stop Camera";
    }
  }

  async startCamera() {
    try {
      const constraints = {
        video: {
          deviceId: this.devices[this.deviceIndex]?.deviceId,
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;
      this.video.play();
      this.scanning = true;
      this.scan();
      this.hideError();
    } catch (error) {
      this.showError("Camera access denied: " + error.message);
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    this.scanning = false;
    this.video.srcObject = null;
  }

  async switchCamera() {
    this.deviceIndex = (this.deviceIndex + 1) % this.devices.length;
    if (this.stream) {
      this.stopCamera();
      await this.startCamera();
    }
  }

  scan() {
    if (!this.scanning) return;

    if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
      this.canvas.height = this.video.videoHeight;
      this.canvas.width = this.video.videoWidth;
      this.canvasContext.drawImage(
        this.video,
        0,
        0,
        this.canvas.width,
        this.canvas.height
      );

      const imageData = this.canvasContext.getImageData(
        0,
        0,
        this.canvas.width,
        this.canvas.height
      );
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        this.handleQRCode(code.data);
      }
    }

    requestAnimationFrame(() => this.scan());
  }

  async handleQRCode(data) {
    try {
      const response = await fetch("/verify/verify_qr/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          registration_id: qrData,
        }),
      });

      const result = await response.json();

      let modalContent = "";
      if (result.status === "success") {
        modalContent = `
                <div class="alert alert-success">
                    <h4>Valid Registration</h4>
                    <p><strong>Name:</strong> ${result.data.full_name}</p>
                    <p><strong>Course:</strong> ${result.data.course}</p>
                    <p><strong>Schedule:</strong> ${result.data.preferred_schedule}</p>
                </div>
            `;
      } else {
        modalContent = `
                <div class="alert alert-danger">
                    <h4>Error</h4>
                    <p>${result.message}</p>
                </div>
            `;
      }

      document.getElementById("scan-result").innerHTML = modalContent;
      new bootstrap.Modal(document.getElementById("result-modal")).show();
    } catch (error) {
      console.error("Error:", error);
      document.getElementById("scan-result").innerHTML = `
            <div class="alert alert-danger">
                <h4>Error</h4>
                <p>An unexpected error occurred. Please try again.</p>
            </div>
        `;
      new bootstrap.Modal(document.getElementById("result-modal")).show();
    }
  }

  showResult(data) {
    const modal = new bootstrap.Modal(document.getElementById("resultModal"));
    const content = document.getElementById("result-content");

    content.innerHTML = `
            <div class="alert alert-success">Valid Registration</div>
            <div class="mb-2"><strong>Name:</strong> ${data.full_name}</div>
            <div class="mb-2"><strong>Email:</strong> ${data.email}</div>
            <div class="mb-2"><strong>Schedule:</strong> ${data.preferred_schedule}</div>
            <div class="mb-2"><strong>Registration Date:</strong> ${data.registration_date}</div>
            <div class="mb-2"><strong>ID:</strong> ${data.registration_id}</div>
        `;

    modal.show();
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.style.display = "block";
  }

  hideError() {
    this.errorMessage.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const scanner = new QRScanner();
  scanner.init();
});
