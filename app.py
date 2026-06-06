import cv2
import time
import os
import threading
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from stego_utils import hide_data_fast, extract_data_fast

# RTMP gecikmelerini (lag) önlemek için OpenCV FFmpeg ayarları (Zero-Latency Flag)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "fflags;nobuffer|analyzeduration;0|probesize;32"

app = Flask(__name__)

# Global değişkenler
current_secret_message = "Merhaba! Bu mesaj varsayilan olarak gizlenmistir."
last_decoded_message = "Henüz veri okunamadı..."
current_camera_id = 1
change_camera_flag = False

class CameraThread(threading.Thread):
    """
    Kamerayı asenkron olarak arka planda sürekli okuyan sınıf.
    Bu sayede eski kareler buffer'da birikmez, her zaman en son (taze) kareyi alırız.
    """
    def __init__(self, src):
        super().__init__()
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        self.latest_frame = None
        self.running = True
        self.daemon = True # Ana program kapanınca bu thread de kapansın

    def run(self):
        while self.running:
            success, frame = self.cap.read()
            if success:
                self.latest_frame = frame
            else:
                time.sleep(0.01)

    def get_frame(self):
        return self.latest_frame
    
    def stop(self):
        self.running = False
        self.cap.release()

cam_thread = None

def start_camera(cam_id):
    global cam_thread
    if cam_thread is not None:
        cam_thread.stop()
        cam_thread.join(timeout=1.0)
    
    cam_thread = CameraThread(cam_id)
    if not cam_thread.cap.isOpened():
        print(f"Uyarı: {cam_id} kaynak açılamadı. Fallback (0) deneniyor.")
        cam_thread.stop()
        cam_thread = CameraThread(0)
    
    cam_thread.start()

def generate_frames():
    global current_secret_message, last_decoded_message, current_camera_id, change_camera_flag, cam_thread
    
    start_camera(current_camera_id)
        
    while True:
        # Eğer arayüzden kamera değiştirme isteği gelirse
        if change_camera_flag:
            start_camera(current_camera_id)
            change_camera_flag = False
            
        frame = cam_thread.get_frame()
        if frame is None:
            # Bağlantı koptuğunda veya kamera gelmediğinde web sitesinin çökmemesi için
            # "Sinyal Yok" ekranı oluşturup tarayıcıya yolluyoruz.
            no_signal_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(no_signal_frame, "KAMERA / YAYIN BULUNAMADI", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(no_signal_frame, "Lutfen Arayuzden Dogru Kaynagi Secin", (50, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
            
            ret, buffer = cv2.imencode('.jpg', no_signal_frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.5)
            continue
            
        # Görüntüye güncel gizli mesajı DWT-QIM ile gömüyoruz
        msg_with_time = f"{current_secret_message} [{time.strftime('%H:%M:%S')}]"
        
        # Bu işlem artık stego_utils içindeki ROI (Region of Interest) sayesinde x16 kat daha hızlı
        encoded_frame = hide_data_fast(frame, msg_with_time)
        
        # Test amaçlı: Gizlenen veriyi anında geri okuyup arayüze göstermek için kaydediyoruz
        last_decoded_message = extract_data_fast(encoded_frame)
        
        # Web tarayıcısında göstermek için çerçeveyi JPEG olarak encode et
        ret, buffer = cv2.imencode('.jpg', encoded_frame)
        frame_bytes = buffer.tobytes()
        
        # MJPEG formatında çerçeveyi yield et
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        # Tarayıcıya FPS sabitlemesi (30 FPS hedefi: ~33ms)
        time.sleep(0.03)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/set_message', methods=['POST'])
def set_message():
    global current_secret_message
    data = request.json
    new_message = data.get('message', '')
    if new_message:
        current_secret_message = new_message
        return jsonify({"status": "success", "message": "Gizli mesaj başarıyla güncellendi!"})
    return jsonify({"status": "error", "message": "Mesaj boş olamaz!"}), 400

@app.route('/api/get_message')
def get_message():
    global last_decoded_message
    return jsonify({"decoded_message": last_decoded_message})

@app.route('/api/set_camera', methods=['POST'])
def set_camera():
    global current_camera_id, change_camera_flag
    data = request.json
    cam_id = data.get('camera_id')
    if cam_id is not None:
        if str(cam_id).startswith('rtmp://'):
            current_camera_id = str(cam_id)
            change_camera_flag = True
            return jsonify({"status": "success", "message": "RTMP Sunucusuna bağlanılıyor..."})
        else:
            try:
                current_camera_id = int(cam_id)
                change_camera_flag = True
                return jsonify({"status": "success", "message": f"Kamera {cam_id} olarak değiştirildi!"})
            except ValueError:
                pass
    return jsonify({"status": "error", "message": "Geçersiz kamera ID'si veya URL'si!"}), 400

if __name__ == '__main__':
    print("Web sunucusu baslatiliyor...")
    print("http://localhost:5000 adresinden arayüze erişebilirsiniz.")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
