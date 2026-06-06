import cv2
import time
from stego_utils import extract_data_fast

def main():
    # Decoder, veriyi gizlediğimiz encoder'ın oluşturduğu Sanal Kamerayı veya
    # OBS'ten doğrudan gelen yayını okuyacak.
    # Kamera numaranızı buradan ayarlayın (genellikle 2, 3 veya 4 olabilir yeni eklenen kameralara göre).
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
            
            # Görüntüyü ekranda göster
            cv2.imshow('Decoder View', frame)
            
            # Karedeki gizli veriyi oku
            start_time = time.time()
            hidden_message = extract_data_fast(frame)
            end_time = time.time()
            
            if hidden_message:
                print(f"[Veri Bulundu - Çözme Süresi: {(end_time - start_time)*1000:.1f}ms] Mesaj: {hidden_message}")
            else:
                pass # Ekranda spam olmaması için boşken yazdırmıyoruz
                
            # 'q' tuşuna basıldığında çık
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("İşlem sonlandırıldı.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
