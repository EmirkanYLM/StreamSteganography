@echo off
title StegoCast Web Sunucusu
echo ===================================================
echo StegoCast Video Steganography Sunucusu Baslatiliyor
echo ===================================================
echo.
echo Lutfen acilan siyah pencereleri kapatmayin!
echo Arayuz tarayicinizda otomatik olarak acilacaktir...
echo.

:: Python Kutuphanelerini (Requirements) Otomatik Yukle
echo Python kutuphaneleri kontrol ediliyor / yukleniyor... Lutfen bekleyin...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [UYARI] pip install komutu calismadi. Lutfen Python'in yuklu oldugundan emin olun.
) else (
    echo Kutuphaneler hazir!
)
echo.

:: RTMP Sunucusunu baslat
echo RTMP Sunucusu kontrol ediliyor...
if not exist "mediamtx\mediamtx.exe" (
    echo MediaMTX RTMP Sunucusu bulunamadi. Otomatik olarak indiriliyor... Lutfen bekleyin...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/bluenviron/mediamtx/releases/download/v1.9.3/mediamtx_v1.9.3_windows_amd64.zip' -OutFile 'mediamtx.zip'"
    powershell -Command "Expand-Archive -Path 'mediamtx.zip' -DestinationPath 'mediamtx' -Force"
    del mediamtx.zip
    echo Indirme basarili!
)

echo RTMP Sunucusu baslatiliyor...
cd mediamtx
start "MediaMTX Server" cmd /c "mediamtx.exe"
cd ..

:: Python sunucusunu (Flask) baslat
echo Web Sunucusu baslatiliyor...
start "StegoCast Server" cmd /c "python app.py & pause"

:: Sunucularin hazir olmasi icin 3 saniye bekle
ping 127.0.0.1 -n 4 > nul

:: Varsayilan web tarayicisinda arayuzu ac
start "" "http://localhost:5000"

exit
