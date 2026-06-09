import cv2
import time
from stego_utils import extract_data_fast

def main():
    
    camera_id = 2
    cap = cv2.VideoCapture(camera_id)
    
    if not cap.isOpened():
        print(f"Hata: {camera_id} ID'li kamera açılamadı. Lütfen doğru kamera numarasını girin.")
        return

    print("Veri okuma işlemi başladı. Okunan mesajlar buraya yazdırılacak.")
    print("Kapatmak için terminalde Ctrl+C yapın veya 'q' tuşuna basın.")
    
    cv2.namedWindow('Decoder View', cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Görüntü okunamadı, bekleniyor...")
                time.sleep(1)
                continue
            
            
            cv2.imshow('Decoder View', frame)
            
            
            start_time = time.time()
            hidden_message = extract_data_fast(frame)
            end_time = time.time()
            
            if hidden_message:
                print(f"[Veri Bulundu - Çözme Süresi: {(end_time - start_time)*1000:.1f}ms] Mesaj: {hidden_message}")
            else:
                pass 
                
           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("İşlem sonlandırıldı.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
