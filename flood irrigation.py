import requests
import serial
import RPi.GPIO as GPIO
import time

# Constants
IMD_API_URL = 'https://api.imd.gov.in/data_endpoint'  # Replace with actual IMD API endpoint
SERIAL_PORT = '/dev/ttyUSB0'  # Adjust based on your setup
RELAY_PIN = 17  # GPIO pin connected to relay

# Thresholds for Kharif crops
THRESHOLDS = {
    'humidity': 60,
    'temperature': 20,
    'moisture': 300  # Adjust based on your sensor's range
}

def get_weather_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data['humidity'], data['temperature']
    else:
        raise Exception("Failed to fetch weather data")

def get_soil_moisture(serial_port):
    ser = serial.Serial(serial_port, 9600)
    moisture_level = ser.readline().strip()
    ser.close()
    return int(moisture_level)

def should_water_crop(humidity, temperature, soil_moisture, thresholds):
    if humidity < thresholds['humidity'] and temperature > thresholds['temperature'] and soil_moisture < thresholds['moisture']:
        return True
    return False

def setup_relay():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initially off

def control_tubewell(turn_on):
    if turn_on:
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn on
    else:
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn off

def main():
    setup_relay()
    
    while True:
        try:
            humidity, temperature = get_weather_data(IMD_API_URL)
            soil_moisture = get_soil_moisture(SERIAL_PORT)
            
            water_crop = should_water_crop(humidity, temperature, soil_moisture, THRESHOLDS)
            control_tubewell(water_crop)
            
            if water_crop:
                while soil_moisture < THRESHOLDS['moisture']:
                    time.sleep(600)  # Check every 10 minutes
                    soil_moisture = get_soil_moisture(SERIAL_PORT)
                control_tubewell(False)
            
            time.sleep(3600)  # Check every hour
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3600)

if _name_ == "_main_":
    main()