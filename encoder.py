import cv2
import pyvirtualcam
import time
from stego_utils import hide_data_fast

def main():
    
    camera_id = 1 
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Hata: {camera_id} ID'li kamera açılamadı. OBS Sanal Kameranın açık olduğundan emin olun.")
        # Fallback to 0 if 1 fails
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
             return

    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    if fps == 0 or fps is None:
        fps = 30 

    print(f"Giriş Kamerası Çözünürlüğü: {width}x{height} @ {fps} FPS")
    print("Veri gizleme işlemi başladı. Kapatmak için terminalde Ctrl+C yapın.")

    secret_message = "Merhaba! Bu mesaj OBS canli yayininin icine gizlenmistir. Zaman: "

    
    try:
        with pyvirtualcam.Camera(width=width, height=height, fps=fps, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            print(f"Sanal Kamera '{cam.device}' basariyla olusturuldu.")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Görüntü okunamadı, bekleniyor...")
                    time.sleep(1)
                    continue
                
                
                current_message = secret_message + str(time.time())
                
                
                encoded_frame = hide_data_fast(frame, current_message)
                
                
                cam.send(encoded_frame)
                
                
                cam.sleep_until_next_frame()
                
    except KeyboardInterrupt:
        print("İşlem sonlandırıldı.")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
