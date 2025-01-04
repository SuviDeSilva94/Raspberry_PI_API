import sds011
import time
import json
import logging
import serial
from flask import Flask, jsonify


# ----- Logging Setup -----
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ----- Serial Configuration -----
# Use hardcoded port for use_query_mode
serial_port = "/dev/ttyUSB0" # or whatever you are using such as "/dev/ttyACM0"
baudrate = 9600  # Usually this is 9600, but check the sensor documentation

# Try creating serial object with error handling
try:
  ser = serial.Serial(serial_port, baudrate)
except serial.SerialException as e:
  logging.error(f"Failed to create serial object: {e}")
  exit() # Exit if no serial object could be created

# ----- Initialize SDS011 -----
try:
    sensor = sds011.SDS011(ser, use_query_mode=True)  # <----- Use serial object AND query mode
    logging.debug("SDS011 Sensor Initialized")
except Exception as e:
    logging.error(f"Failed to initialize sensor: {e}")
    exit()

def get_sensor_data():
    """Reads data from the SDS011 sensor."""
    try:
        pm25, pm10 = sensor.query()
        logging.debug(f"Read data: PM2.5 = {pm25}, PM10 = {pm10}")
        return {"pm25": pm25, "pm10": pm10}
    except Exception as e:
        logging.error(f"Error reading from sensor: {e}")
        return None


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