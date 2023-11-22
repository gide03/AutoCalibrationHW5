# Auto calibration meter HW5

How to use:

1. Setup python environment. Please consider to use python virtual environment. If it is already exist, activate it
2. Install the requirements. `> pip install -r requirements.txt`
3. Run the script

## How the script works

1. Setting Geny, 230 Volt, 20 A, 60 degree, 3 Phase.
2. Masukkan nilai referensi power supply.
3. Pembacaan object 0_128_96_14_80_255 - CalibrationData.
4. Pembacaan voltage RMS setiap detik, 5 kali, nilai disimpan.
5. Execute kalibrasi voltage gain.
6. Pembacaan arus RMS setiap detik, 5 kali, nilai disimpan.
7. Execute kalibrasi arus gain.
8. Pembacaan nilai active power setiap detik, 5 kali, nilai disimpan.
9. Execute kalibrasi power active gain.
10. Pembacaan nilai reactive power setiap detik, 5 kali, nilai disimpan.
11. Execute kalibrasi power reactive gain.
12. Pembacaan nilai apparent power setiap detik, 5 kali, nilai disimpan.
13. Execute kalibrasi power apparent gain.
14. Pembacaan object 0_128_96_14_80_255 - CalibrationData.
