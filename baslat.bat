@echo off
title StegoCast Web Sunucusu
echo ===================================================
echo StegoCast Video Steganography Sunucusu Baslatiliyor
echo ===================================================
echo.
echo Lutfen acilan siyah pencereleri kapatmayin!
echo Arayuz tarayicinizda otomatik olarak acilacaktir...
echo.

:: RTMP Sunucusunu baslat
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
