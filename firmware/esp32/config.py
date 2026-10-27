# Copia este archivo y rellénalo. La clave de la API sale de claves_demo.json (o del alta del nodo).
WIFI_SSID = "mi-wifi"          # en clase: usa el punto de acceso del móvil
WIFI_PASS = "mi-clave"
API_URL = "http://192.168.1.50:8000"  # IP del ordenador que corre la app
API_KEY = "clave-del-nodo"
# Ids de sensor en la base de datos (parcela 1 del seed: 1 temp, 2 aire, 3 suelo, 4 luz)
SENSOR_IDS = {"temperature": 1, "air_humidity": 2, "soil_moisture": 3, "light": 4}
INTERVALO_S = 30
# Calibración del sensor de suelo: lectura ADC (0-65535) con el sensor al aire y en un vaso de agua
SUELO_AIRE = 52000    # = 0 %
SUELO_AGUA = 21000    # = 100 %
PIN_DHT, PIN_SUELO, PIN_SDA, PIN_SCL = 4, 34, 21, 22
