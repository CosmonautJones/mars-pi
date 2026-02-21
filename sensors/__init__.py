"""
sensors package — grow tent environmental sensors.

Currently a placeholder.  Once the BME280 is wired up on I2C, import and
call `bme280.read()` here and include its data in the returned dict.
"""


def read_sensors() -> dict:
    """
    Return the latest sensor readings as a plain dict.

    Fields (once hardware is attached):
      temperature_c  — float, degrees Celsius
      humidity_pct   — float, relative humidity %
      pressure_hpa   — float, barometric pressure hPa

    Returns an empty dict until the BME280 module is implemented.
    """
    # TODO: uncomment when BME280 is wired up
    # from sensors.bme280 import read as bme_read
    # return bme_read()
    return {}

