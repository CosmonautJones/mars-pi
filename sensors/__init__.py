"""
sensors package — grow tent environmental sensors.

Reads BME280 (temperature, humidity, pressure) over I2C.
Returns {} gracefully if the sensor is disconnected or fails.
"""

import logging

log = logging.getLogger(__name__)


def read_sensors() -> dict:
    """
    Return the latest sensor readings as a plain dict.

    Fields:
      temperature_c  — float, degrees Celsius
      humidity_pct   — float, relative humidity %
      pressure_hpa   — float, barometric pressure hPa

    Returns an empty dict if the sensor is unavailable.
    """
    try:
        from sensors.bme280 import read as bme_read
        return bme_read()
    except Exception as exc:
        log.warning("BME280 read failed: %s", exc)
        return {}

