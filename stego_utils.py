import numpy as np
import cv2
import pywt


DELIMITER = b"#####END#####"


DELTA = 24  
REPETITION = 5  
WAVELET = 'haar'
ROI_SIZE = 512  

def hide_data_fast(image, secret_data_str):

    if not secret_data_str:
        return image
        
    secret_data_bytes = secret_data_str.encode('utf-8') + DELIMITER
    bits = np.unpackbits(np.frombuffer(secret_data_bytes, dtype=np.uint8))
    
    
    repeated_bits = np.repeat(bits, REPETITION)
    
    
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    
    h, w = yuv_image.shape[:2]
    crop_h = min(h, ROI_SIZE)
    crop_w = min(w, ROI_SIZE)
    
    y_channel = yuv_image[0:crop_h, 0:crop_w, 0].astype(np.float32)
    
    
    coeffs2 = pywt.dwt2(y_channel, WAVELET)
    LL, (LH, HL, HH) = coeffs2
    
    
    LH_flat = LH.ravel()
    
    if len(repeated_bits) > len(LH_flat):
        raise ValueError("Gizlenecek veri, DWT bant kapasitesini aşıyor!")
        
    
    N = len(repeated_bits)
    target_coeffs = LH_flat[:N]
    
    
    quantized = np.round(target_coeffs / DELTA)
    current_bits = np.mod(np.abs(quantized), 2)
    
    
    diff = np.abs(repeated_bits - current_bits)
    
   
    change_dir = np.sign(target_coeffs - quantized * DELTA)
    change_dir[change_dir == 0] = 1 # 0 olmasını engelle
    
    
    new_quantized = quantized + diff * change_dir
    
    
    LH_flat[:N] = new_quantized * DELTA
    
   
    LH_new = LH_flat.reshape(LH.shape)
    new_y_channel = pywt.idwt2((LL, (LH_new, HL, HH)), WAVELET)
    
   
    new_y_channel = new_y_channel[:crop_h, :crop_w]
    
   
    new_y_channel = np.clip(new_y_channel, 0, 255).astype(np.uint8)
    
    
    encoded_yuv = yuv_image.copy()
    encoded_yuv[0:crop_h, 0:crop_w, 0] = new_y_channel
    encoded_image = cv2.cvtColor(encoded_yuv, cv2.COLOR_YUV2BGR)
    
    return encoded_image

def extract_data_fast(image):
    """
    DWT ve QIM kullanılarak gizlenmiş veriyi okur.
    Majority Voting (Çoğunluk oyu) ile hataları düzeltir.
    """
   
    yuv_image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    
    h, w = yuv_image.shape[:2]
    crop_h = min(h, ROI_SIZE)
    crop_w = min(w, ROI_SIZE)
    
    y_channel = yuv_image[0:crop_h, 0:crop_w, 0].astype(np.float32)
    
    
    coeffs2 = pywt.dwt2(y_channel, WAVELET)
    LL, (LH, HL, HH) = coeffs2
    
    LH_flat = LH.ravel()
    
   
    quantized = np.round(LH_flat / DELTA)
    extracted_bits = np.mod(np.abs(quantized), 2).astype(np.uint8)
    
    
    valid_len = (len(extracted_bits) // REPETITION) * REPETITION
    reshaped_bits = extracted_bits[:valid_len].reshape(-1, REPETITION)
    
   
    voted_bits = np.median(reshaped_bits, axis=1).astype(np.uint8)
    
    
    all_bytes = np.packbits(voted_bits)
    data = all_bytes.tobytes()
    
   
    idx = data.find(DELIMITER)
    
    if idx != -1:
        return data[:idx].decode('utf-8', errors='ignore')
    
    return ""
