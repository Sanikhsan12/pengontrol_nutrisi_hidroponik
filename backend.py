# library
import mysql.connector as conn
from datetime import datetime as date
from main import monitorHidroponik
import time 

# ! inisialisasi koneksi ke database
def koneksi():
    try:
        koneksiDB = conn.connect(
            host='localhost',
            port='3307',
            user='root',
            password='',
            database='hidroponik'
        )

        if koneksiDB.is_connected():
            print('berhasil terhubung ke database')
            return koneksiDB
    except Exception as e:
        print(f'gagal terhubung ke database : {e}')
        print(e)

def post_data():
    db = koneksi()
    data = monitorHidroponik()
    if db:
        while True:
            try:
                cursor = db.cursor()
                sql = (f"INSERT INTO data_monitoring (kadar_soil,kondisi_soil,ph,kondisi_ph,kalsium,kalium,magnesium,nitrogen,timestamp) 
                        VALUES {data.soil_moisture, data.kondisi_soil, data.ph, data.kondisi_ph, data.kalsium, data.kalium, data.magnesium, data.nitrogen, date.now()}")
            
                cursor.execute(sql)
                db.commit()
                time.sleep(5)
            except Exception as e:
                print(f'gagal memasukkan data ke database : {e}')
                print(e)
