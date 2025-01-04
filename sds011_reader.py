import sds011
import time
import json
import logging
import serial

# ----- Logging Setup -----
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# ----- Serial Configuration -----
# Adjust serial_port and baudrate based on your connections and the sensor specs
serial_port = "/dev/ttyS0" # Usually this is ttyS0, you may have to use ttyAMA0
baudrate = 9600 # Usually this is 9600, but check the sensor documentation

# Try creating serial object with error handling
try:
  ser = serial.Serial(serial_port, baudrate)
except serial.SerialException as e:
  logging.error(f"Failed to create serial object: {e}")
  exit() # Exit if no serial object could be created

# ----- Initialize SDS011 -----
try:
    sensor = sds011.SDS011(ser)
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

def create_json_output():
  """Creates a JSON string containing sensor data."""
  data = get_sensor_data()
  if data:
    return json.dumps(data)
  else:
    return json.dumps({"error": "Could not retrieve sensor data"})

if __name__ == "__main__":
  while True:
    print(create_json_output())
    time.sleep(10)  # Read data every 10 seconds