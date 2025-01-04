import sds011
import time
import json
import logging
import serial
from flask import Flask, jsonify
import re

# ----- Logging Setup -----
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ----- Serial Configuration -----
# Find the usb serial port - This pattern may need to be adjusted based on the OS
usb_pattern = re.compile(r"/dev/ttyUSB\d+")

# Function to find a serial port that matches the USB pattern
def find_serial_port():
  for dev in serial.tools.list_ports.comports():
    if usb_pattern.match(dev.device):
      return dev.device
  return None

serial_port = find_serial_port()

if not serial_port:
    logging.error("Could not find a USB-to-Serial device")
    exit()
else:
    logging.debug(f"Found Serial Port: {serial_port}")
baudrate = 9600 # Usually this is 9600, but check the sensor documentation

# Try creating serial object with error handling
try:
  ser = serial.Serial(serial_port, baudrate)
except serial.SerialException as e:
  logging.error(f"Failed to create serial object: {e}")
  exit() # Exit if no serial object could be created


# ----- Initialize SDS011 -----
try:
  sensor = sds011.SDS011(ser, use_query_mode=True)
  logging.debug("SDS011 Sensor Initialized")
except Exception as e:
    logging.error(f"Failed to initialize sensor: {e}")
    exit()


def get_sensor_data():
    """Reads data from the SDS011 sensor, controlling sleep mode and handling errors."""
    logging.debug("get_sensor_data: Starting")
    try:
        logging.debug("get_sensor_data: Waking up the sensor")
        sensor.sleep = False
        logging.debug("get_sensor_data: Before sensor.query()")
        query_result = sensor.query() # <----- Get the query result
        logging.debug(f"get_sensor_data: After sensor.query() - Result = {query_result}")

        if isinstance(query_result, tuple) and len(query_result) == 2: # <----- check if tuple
            pm25, pm10 = query_result
            logging.debug(f"get_sensor_data: After sensor.query() - PM2.5 = {pm25}, PM10 = {pm10}")
            return {"pm25": pm25, "pm10": pm10}
        else:
           logging.error(f"get_sensor_data: Query data is not iterable, result = {query_result}")
           return None

    except Exception as e:
        logging.error(f"get_sensor_data: Error reading from sensor: {e}")
        return None
    finally:
        logging.debug("get_sensor_data: Putting sensor to sleep")
        sensor.sleep = True


app = Flask(__name__)

@app.route('/airquality', methods=['GET'])
def get_air_quality():
    """
    Returns JSON data containing PM2.5 and PM10 values from the SDS011 sensor.
    """
    data = get_sensor_data()
    if data:
      return jsonify(data), 200
    else:
       return jsonify({"error": "Could not retrieve sensor data"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)