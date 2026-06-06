import cv2
import pyvirtualcam
import time
from stego_utils import hide_data_fast

def main():
    # OBS Virtual Camera genellikle 0, 1 veya 2 numaralı ID'de bulunur.
    # Kendi sisteminizde OBS Sanal Kamerasının numarasını bulmak için denemeniz gerekebilir.
    # Varsayılan olarak 0 ana web kamerasını, 1 ise genelde OBS'i açar.
    camera_id = 1 
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Hata: {camera_id} ID'li kamera açılamadı. OBS Sanal Kameranın açık olduğundan emin olun.")
        # Fallback to 0 if 1 fails
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
             return

    # Kameranın çözünürlüğünü ve FPS'ini alalım
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps == 0 or fps is None:
        fps = 30 # Varsayılan FPS

    print(f"Giriş Kamerası Çözünürlüğü: {width}x{height} @ {fps} FPS")
    print("Veri gizleme işlemi başladı. Kapatmak için terminalde Ctrl+C yapın.")

    secret_message = "Merhaba! Bu mesaj OBS canli yayininin icine gizlenmistir. Zaman: "

    # pyvirtualcam ile yeni bir sanal kamera oluşturuyoruz.
    # Bu kamerayı Discord, Zoom veya başka bir programda kaynak olarak seçebilirsiniz.
    try:
        with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            print(f"Sanal Kamera '{cam.device}' basariyla olusturuldu.")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Görüntü okunamadı, bekleniyor...")
                    time.sleep(1)
                    continue
                
                # Dinamik olarak mesajı güncelleyelim ki her karede değiştiğini görelim
                current_message = secret_message + str(time.time())
                
                # Kareye veriyi gizle (çok hızlı numpy fonksiyonumuz)
                encoded_frame = hide_data_fast(frame, current_message)
                
                # pyvirtualcam RGB değil BGR formatında da gönderebilir, BGR formatı kullandık
                cam.send(encoded_frame)
                
                # FPS'i tutturmak için bekle
                cam.sleep_until_next_frame()
                
    except KeyboardInterrupt:
        print("İşlem sonlandırıldı.")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
