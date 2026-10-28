"""Nodo Agrotech para ESP32 (MicroPython). Lee 4 magnitudes cada 30 s y las envía a la API.

Si cae el WiFi guarda las lecturas en memoria y las manda al volver (máx. MAX_PENDIENTES).
Volcado: ver docs/hardware.md.
"""
import time

import dht
import machine
import network
import ntptime
import urequests

import config

MAX_PENDIENTES = 200
pendientes = []

sensor_dht = dht.DHT22(machine.Pin(config.PIN_DHT))
suelo = machine.ADC(machine.Pin(config.PIN_SUELO))
suelo.atten(machine.ADC.ATTN_11DB)
i2c = machine.I2C(0, sda=machine.Pin(config.PIN_SDA), scl=machine.Pin(config.PIN_SCL))
BH1750 = 0x23


def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(1)
    return wlan.isconnected()


def hora_utc():
    t = time.gmtime()
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % t[:6]


def humedad_suelo():
    """Media de 5 lecturas (filtra picos) pasada a % con la calibración."""
    media = sum(suelo.read_u16() for _ in range(5)) / 5
    pct = (config.SUELO_AIRE - media) * 100 / (config.SUELO_AIRE - config.SUELO_AGUA)
    return round(min(100.0, max(0.0, pct)), 1)


def luz_lx():
    i2c.writeto(BH1750, b"\x20")  # medida única en alta resolución
    time.sleep_ms(180)
    d = i2c.readfrom(BH1750, 2)
    return round(((d[0] << 8) | d[1]) / 1.2)


def leer():
    sensor_dht.measure()
    ts = hora_utc()
    valores = (
        ("temperature", sensor_dht.temperature(), "ºC"),
        ("air_humidity", sensor_dht.humidity(), "%"),
        ("soil_moisture", humedad_suelo(), "%"),
        ("light", luz_lx(), "lx"),
    )
    return [{"sensor_id": config.SENSOR_IDS[t], "timestamp": ts, "type": t, "value": v, "unit": u}
            for t, v, u in valores]


def enviar(lectura):
    try:
        r = urequests.post("%s/api/sensors/%d/data" % (config.API_URL, lectura["sensor_id"]),
                           json=lectura, headers={"X-API-Key": config.API_KEY})
        ok = r.status_code in (201, 422)  # 422 = dato inválido: reenviarlo no lo arreglaría
        r.close()
        return ok
    except OSError:
        return False


def ciclo():
    if not conectar_wifi():
        pendientes.extend(leer())
        del pendientes[:-MAX_PENDIENTES]
        return
    try:
        ntptime.settime()  # el contrato exige hora UTC fiable
    except OSError:
        pass
    pendientes.extend(leer())
    while pendientes and enviar(pendientes[0]):
        pendientes.pop(0)
    del pendientes[:-MAX_PENDIENTES]


while True:
    try:
        ciclo()
    except Exception as e:  # un sensor mal conectado no debe parar el nodo
        print("error:", e)
    time.sleep(config.INTERVALO_S)
