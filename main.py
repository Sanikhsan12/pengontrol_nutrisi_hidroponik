# library
import time
import Adafruit_ADS1x15 as adafruit
import flask
from flask import Flask, jsonify
import threading
import random
from backend import post_data, koneksi as conn

# ! inisialisasi pin / channel module sensor
pin_soil_moisture = 0
pin_ph = 1

# ! inisialisasi adc
# ? untuk membaca nilai hasil deteksi dan dikoneversi dari analog ke digital
adc = adafruit.ADS1115()

# ! nilai patokan kalibrasi
soil_moisture_min = 0 # nilai adc kelembapan saat kering
soil_moisture_max = 26000 # nilai adc kelembapan saat basah
ph_min = 0 # nilai adc ph terendah
ph_max = 26000 # nilai adc ph tertinggi

# * class untuk menyimpan data monitoring
class monitorHidroponik:
    def __init__(self):
        self.kondisi_soil = 'Normal' # kondisi default kelembapan tanah
        self.soil_moisture = 0
        self.kondisi_ph = 'Normal' # kondisi default ph
        self.ph = 0
        self.kalsium = monitorHidroponik.randomizer(0, 100)
        self.kalium = monitorHidroponik.randomizer(0, 100)
        self.magnesium = monitorHidroponik.randomizer(0, 100)
        self.nitrogen = monitorHidroponik.randomizer(0, 100)
        self.running = True

    def randomizer(angka_awal, angka_akhir):
        time.sleep(5)
        angka = random.uniform(angka_awal, angka_akhir)
        return angka

    def baca_soilMoist(self):
        nilai_deteksi_soil = adc.read_adc(pin_soil_moisture, gain=1)
        nilai_presentasi_soil = 100 - (nilai_deteksi_soil - soil_moisture_min) / (soil_moisture_max - soil_moisture_min) * 100

        # ? kondisi kelembapan tanah
        if nilai_presentasi_soil <= 30 :
            self.kondisi_soil = 'Kering'
        elif nilai_presentasi_soil > 30 and nilai_presentasi_soil <= 60:
            self.kondisi_soil = 'Normal'
        elif nilai_presentasi_soil > 60 and nilai_presentasi_soil <= 80:
            self.kondisi_soil = 'Basah'
        else:
            self.kondisi_soil = 'Terlalu Basah'

        return max(0, min(100, nilai_presentasi_soil))

    def baca_ph(self):
        nilai_deteksi_ph = adc.read_adc(pin_ph, gain=1)
        nilai_presentasi_ph = (nilai_deteksi_ph - ph_min) * (14 / (ph_max - ph_min))

        # ? kondisi ph
        if nilai_presentasi_ph < 7:
            self.kondisi_ph = 'Asam'
        elif nilai_presentasi_ph > 7:
            self.kondisi_ph = 'Basa'
        else:
            self.kondisi_ph = 'Normal'

        return round(nilai_presentasi_ph, 1)

    def monitoringSensor(self):
        while self.running:
            self.soil_moisture = self.baca_soilMoist()
            self.ph = self.baca_ph()

            print(f'kelembapan tanah: {self.soil_moisture}% dengan kondisi {self.kondisi_soil}, ph: {self.ph} dengan kondisi {self.kondisi_ph}')
            conn()
            post_data()
            time.sleep(5)

    def run_monitoring(self):
        monitor = threading.Thread(target=self.monitoringSensor)
        monitor.daemon = True
        monitor.start()

# ! init flask
app = Flask(__name__, template_folder='view', static_folder='view')
hidroponik = monitorHidroponik()

# ! routing
@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify({
        'soil_moisture': hidroponik.soil_moisture,
        'kondisi_soil': hidroponik.kondisi_soil,
        'ph': hidroponik.ph,
        'kondisi_ph': hidroponik.kondisi_ph,
        'kalsium': hidroponik.kalsium,
        'kalium': hidroponik.kalium,
        'magnesium': hidroponik.magnesium,
        'nitrogen': hidroponik.nitrogen
    })

def main():
    hidroponik.run_monitoring()
    app.run(host='0.0.0.0', port=5000)

# ! run app
if __name__ == '__main__':
    main()