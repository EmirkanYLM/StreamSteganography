import numpy as np
import cv2
import pywt

# Benzersiz bir ayırıcı (delimiter) kullanıyoruz.
DELIMITER = b"#####END#####"

# H.264 sıkıştırmasına karşı dayanıklılık parametreleri
DELTA = 24  # QIM adım aralığı. Büyüdükçe dayanıklılık artar, görünürlük artar (Tavsiye edilen: 16-32)
REPETITION = 5  # Her bitin kaç kere arka arkaya yazılacağı (Majority vote ile hata düzeltme)
WAVELET = 'haar'
ROI_SIZE = 512  # İşlemci darboğazını (lag) engellemek için sadece sol üst köşedeki x piksellik alanı işleyeceğiz

def hide_data_fast(image, secret_data_str):
    """
    DWT (Ayrık Dalgacık Dönüşümü) ve QIM kullanarak görüntüye veri gizler.
    Bu yöntem kayıplı (lossy) sıkıştırmalara (H.264 vb.) karşı dayanıklıdır.
    """
    if not secret_data_str:
        return image
        
    secret_data_bytes = secret_data_str.encode('utf-8') + DELIMITER
    bits = np.unpackbits(np.frombuffer(secret_data_bytes, dtype=np.uint8))
    
    # Her biti gürültüye karşı korumak için REPETITION kadar çoğaltıyoruz
    # Örn: 101 -> 11111 00000 11111 (REPETITION=5 için)
    repeated_bits = np.repeat(bits, REPETITION)
    
    # H.264 sıkıştırmasına karşı en dayanıklı olan Y-Luma (Parlaklık) kanalını kullanmak için
    # görüntüyü BGR'den YUV renk uzayına çeviriyoruz.
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    # Performans (Zero-Latency) için ROI (Region of Interest) Kesimi
    h, w = yuv_image.shape[:2]
    crop_h = min(h, ROI_SIZE)
    crop_w = min(w, ROI_SIZE)
    
    y_channel = yuv_image[0:crop_h, 0:crop_w, 0].astype(np.float32)
    
    # Sadece 512x512'lik ufak bir alana 2 Boyutlu DWT uygula
    coeffs2 = pywt.dwt2(y_channel, WAVELET)
    LL, (LH, HL, HH) = coeffs2
    
    # Veriyi Orta frekans olan LH (Yatay detaylar) bandına gömeceğiz
    LH_flat = LH.ravel()
    
    if len(repeated_bits) > len(LH_flat):
        raise ValueError("Gizlenecek veri, DWT bant kapasitesini aşıyor!")
        
    # Sadece veriyi gömeceğimiz kısmı al
    N = len(repeated_bits)
    target_coeffs = LH_flat[:N]
    
    # QIM (Quantization Index Modulation)
    quantized = np.round(target_coeffs / DELTA)
    current_bits = np.mod(np.abs(quantized), 2)
    
    # Bitlerin olması gereken ile mevcut durumlarının farkı (1 ise değişmeli, 0 ise aynı kalmalı)
    diff = np.abs(repeated_bits - current_bits)
    
    # Katsayıyı en az mesafeyle değiştirmek için eklenecek/çıkarılacak yönü bul
    change_dir = np.sign(target_coeffs - quantized * DELTA)
    change_dir[change_dir == 0] = 1 # 0 olmasını engelle
    
    # Değişmesi gereken piksellerde quantize değerini tek/çift duruma göre kaydır
    new_quantized = quantized + diff * change_dir
    
    # Yeni katsayıları hesapla ve yerine koy
    LH_flat[:N] = new_quantized * DELTA
    
    # LH'yi orijinal boyutuna getir ve IDWT ile görüntüyü yeniden oluştur
    LH_new = LH_flat.reshape(LH.shape)
    new_y_channel = pywt.idwt2((LL, (LH_new, HL, HH)), WAVELET)
    
    # Boyutlarda 1 piksellik kaymalar olabilir (dwt padding'inden dolayı), bunu düzeltelim
    new_y_channel = new_y_channel[:crop_h, :crop_w]
    
    # Y kanalını 0-255 arasına kırp (clipping) ve uint8'e dönüştür
    new_y_channel = np.clip(new_y_channel, 0, 255).astype(np.uint8)
    
    # YUV görüntüsünün SADECE ROI BÖLGESİNDEKİ Y kanalını yenisiyle değiştir ve tekrar BGR'ye çevir
    encoded_yuv = yuv_image.copy()
    encoded_yuv[0:crop_h, 0:crop_w, 0] = new_y_channel
    encoded_image = cv2.cvtColor(encoded_yuv, cv2.COLOR_YUV2BGR)
    
    return encoded_image

def extract_data_fast(image):
    """
    DWT ve QIM kullanılarak gizlenmiş veriyi okur.
    Majority Voting (Çoğunluk oyu) ile hataları düzeltir.
    """
    # Görüntüyü YUV'ye çevirip Y-Luma kanalını alıyoruz
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    h, w = yuv_image.shape[:2]
    crop_h = min(h, ROI_SIZE)
    crop_w = min(w, ROI_SIZE)
    
    y_channel = yuv_image[0:crop_h, 0:crop_w, 0].astype(np.float32)
    
    # DWT uygula ve LH bandını al
    coeffs2 = pywt.dwt2(y_channel, WAVELET)
    LL, (LH, HL, HH) = coeffs2
    
    LH_flat = LH.ravel()
    
    # Tüm LH katsayılarından bitleri oku (QIM Demodulation)
    quantized = np.round(LH_flat / DELTA)
    extracted_bits = np.mod(np.abs(quantized), 2).astype(np.uint8)
    
    # Çoğunluk oylaması (Majority Voting) için veriyi yeniden şekillendir
    # Son artıkları (REPETITION'ın tam katı olmayan kısmı) kırp
    valid_len = (len(extracted_bits) // REPETITION) * REPETITION
    reshaped_bits = extracted_bits[:valid_len].reshape(-1, REPETITION)
    
    # Her satırdaki en çok geçen biti al (0 veya 1)
    voted_bits = np.median(reshaped_bits, axis=1).astype(np.uint8)
    
    # Bitleri byte'lara dönüştür
    all_bytes = np.packbits(voted_bits)
    data = all_bytes.tobytes()
    
    # Bitiş işaretini (delimiter) ara
    idx = data.find(DELIMITER)
    
    if idx != -1:
        return data[:idx].decode('utf-8', errors='ignore')
    
    return ""
