# 🕵️ StegoCast: Zero-Latency Video Steganography

**StegoCast** is a high-performance, zero-latency live video steganography system. It uses advanced **DWT (Discrete Wavelet Transform)** and **QIM (Quantization Index Modulation)** algorithms to embed invisible text data into live video streams. 

Unlike traditional LSB (Least Significant Bit) methods, StegoCast is highly resilient to H.264 video compression, making it perfect for real-world streaming environments like **OBS Studio** or RTMP broadcasting.

![StegoCast UI](https://img.shields.io/badge/UI-Modern_Glassmorphism-blue) ![Zero-Latency](https://img.shields.io/badge/Latency-Zero_Delay-brightgreen) ![Python](https://img.shields.io/badge/Python-3.x-yellow)

---

## ✨ Features

*   **H.264 Resilient:** Embeds data in the Y-Luma channel's mid-frequency (LH) bands using Wavelets, surviving aggressive video compression.
*   **Zero-Latency Optimization:** Utilizes multi-threading and localized ROI (Region of Interest) processing to drop mathematical load by 16x, ensuring 0 seconds of video buffer delay.
*   **Direct OBS & RTMP Support:** Captures video directly from OBS Virtual Camera or hosts its own automated RTMP ingest server (`mediamtx`).
*   **Modern Web UI:** A beautiful, responsive Flask-based interface with dark mode, full-screen support, and a live "Hacker-style" decoder panel to monitor the embedded data.
*   **Zero-Config Setup:** Fully automated startup scripts download missing dependencies (like the RTMP server) on the fly.

---

## 🚀 Quick Start (Windows)

The easiest way to run the project is using the automated batch script.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/StegoCast.git
    cd StegoCast
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Start the server:**
    Simply double-click the **`baslat.bat`** file. 
    *   *Note: On first run, it will automatically download the required MediaMTX RTMP server in the background.*

---

## 🎥 How to Use with OBS Studio

You can route your video into StegoCast using two methods:

### Method A: OBS Virtual Camera (Easiest)
1. Open OBS Studio and set up your scene.
2. Click the **"Start Virtual Camera"** button in OBS.
3. Open the StegoCast Web UI (`http://localhost:5000`).
4. Select `Kamera ID: 1 (Sanal Kamera)` from the dropdown.

### Method B: RTMP Streaming (For Networked Setups)
1. Double-click `baslat.bat` to ensure the background RTMP server is running.
2. In OBS, go to **Settings > Stream**.
3. Set Service to `Custom`, Server to `rtmp://localhost:1935/live`, and Stream Key to `obs`.
4. Click **"Start Streaming"** in OBS.
5. In the StegoCast Web UI, select the `RTMP Sunucusundan Al` option.

---

## 🧠 Technical Architecture

*   **DWT-QIM:** The algorithm converts BGR frames to YUV, isolates the Y (Luma) channel, and applies a 2D Haar Wavelet Transform. Data bits are modulated into the Quantization indices of the `LH` (Horizontal Details) band.
*   **Error Correction:** Uses majority voting (repetition codes) to ensure 100% data recovery even if the stream undergoes minor packet loss or noise.
*   **Buffer Flushing:** A dedicated asynchronous Python thread constantly flushes the `cv2.VideoCapture` buffer to prevent FFmpeg frame-queue buildup.

---

## 📜 License
This project is open-source and available under the MIT License.
