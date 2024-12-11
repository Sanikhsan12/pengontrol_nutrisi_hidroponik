# library
import time
import flask
from flask import Flask, jsonify
import threading
import random
import RPi.GPIO as GPIO
from backend import post_data, koneksi as conn

# ! Pengaturan GPIO
GPIO.setmode(GPIO.BCM)
pin_soil_moisture = 17  # * Ganti dengan pin GPIO yang sesuai
pin_ph = 18  # * Ganti dengan pin GPIO yang sesuai

# * class untuk menyimpan data monitoring
class monitorHidroponik:
    def __init__(self):
        GPIO.setup(pin_soil_moisture, GPIO.IN)
        GPIO.setup(pin_ph, GPIO.IN)

        self.kondisi_soil = 'Normal' # * kondisi default kelembapan tanah
        self.soil_moisture = 0 # * kelembapan tanah default
        self.kondisi_ph = 'Normal' # * kondisi default ph
        self.ph = 0 # * ph default
        self.kalsium = monitorHidroponik.randomizer(0, 100)
        self.kalium = monitorHidroponik.randomizer(0, 100)
        self.magnesium = monitorHidroponik.randomizer(0, 100)
        self.nitrogen = monitorHidroponik.randomizer(0, 100)
        self.running = True

    @staticmethod
    def randomizer(angka_awal, angka_akhir):
        time.sleep(5)
        angka = random.uniform(angka_awal, angka_akhir)
        return angka

    def sampling(self,pin,index_sampling=10,delay=0.5):
        read=[]
        for i in range(index_sampling):
            read.append(GPIO.input(pin))
            time.sleep(delay)
        return read

    def baca_soilMoist(self):
        readings = self.sampling(pin_soil_moisture)

        presentasi = (readings.count(GPIO.HIGH) / len(readings)) * 100

        # ? kondisi kelembapan tanah
        if presentasi <= 30 :
            self.kondisi_soil = 'Kering'
            self.soil_moisture = 10
        elif 30 < presentasi <= 60:
            self.kondisi_soil = 'Normal'
            self.soil_moisture = 50
        elif 60 < presentasi <= 80:
            self.kondisi_soil = 'Basah'
            self.soil_moisture = 70
        else:
            self.kondisi_soil = 'Terlalu Basah'
            self.soil_moisture = 90

        return self.soil_moisture
    
    def baca_ph(self):
        readings = self.sampling(pin_ph)

        kadar = (readings.count(GPIO.HIGH) / len(readings)) * 100

        # ? kondisi ph
        if kadar < 7:
            self.kondisi_ph = 'Asam'
            self.ph = 5
        elif kadar > 7:
            self.kondisi_ph = 'Basa'
            self.ph = 9
        else:
            self.kondisi_ph = 'Normal'
            self.ph = 7

        return self.ph

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

    def __del__(self):
        # Membersihkan pengaturan GPIO saat objek dihapus
        GPIO.cleanup()

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