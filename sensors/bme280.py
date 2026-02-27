"""BME280 I2C sensor reader for mars-pi."""
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

_sensor = None


def _get_sensor():
    global _sensor
    if _sensor is None:
        i2c = busio.I2C(board.SCL, board.SDA)
        _sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    return _sensor


def read():
    """Return dict with temperature_c, humidity_pct, pressure_hpa."""
    s = _get_sensor()
    return {
        "temperature_c": round(s.temperature, 1),
        "humidity_pct": round(s.humidity, 1),
        "pressure_hpa": round(s.pressure, 1),
    }
