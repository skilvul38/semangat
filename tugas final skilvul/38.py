import requests
import time
import serial
import string
import pynmea2
import math
import random
import RPi.GPIO as GPIO

TOKEN = "BBFF-kb8dIvg20BT5WZt0LZJLdT23tgl09v"  # Put your TOKEN here
DEVICE_LABEL = "demo"  # Put your device label here 
VARIABLE_LABEL_SWITCH = "switch"  # Put your first variable label here
VARIABLE_LABEL_GPS = "gps"  # Put your second variable label here
port = "/dev/ttyAMA0"

BUZZER_PIN = 17

ubidots_url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/{VARIABLE_LABEL_SWITCH}"
headers = {
    "X-Auth-Token": TOKEN,
    "Content-Type": "application/json"
}

lat = '1.0458837'
lng = '99.7409571'

def build_payload(variable_gps):
    global lat, lng
    
    payload = {variable_gps: {"value": 1, "context": {"lat": lat, "lng": lng}}}

    return payload

def post_request(payload):
    # Creates the headers for the HTTP requests
    global headers
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    status = 400
    attempts = 0
    while (status >= 400 and attempts <= 5):
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True

def get_switch_data():
	response = requests.get(ubidots_url, headers=headers)
	switch_value = response.json()['last_value']['value']
	
	return switch_value

def buzzer_control(switch_value):
    if(switch_value == 1):
        GPIO.output(BUZZER_PIN, 1)
        time.sleep(0.5)
        GPIO.output(BUZZER_PIN, 0)
        time.sleep(0.5)
    else:
        GPIO.output(BUZZER_PIN, 0)
        time.sleep(1)
        
    
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)


if __name__ == '__main__':
	setup()
	gps_val = ''
	#lat = ''
	#lng = ''
	while (True):
		# Read switch data and control buzzer
		switch_value = get_switch_data()
        
		buzzer_control(switch_value)
		
		# Read data GPS
		ser = serial.Serial(port, baudrate=9600, timeout=0.5)
		dataout = pynmea2.NMEAStreamReader()
		#newdata = ser.readline().decode('utf-8').strip()
		newdata = ''

		if newdata[0:6] == "$GPRMC":
			newmsg = pynmea2.parse(newdata)
			lat = newmsg.latitude
			lng = newmsg.longitude
		gps_val = "Latitude=" + str(lat) + " and Longitude=" + str(lng)
		
		# Print data
		print(f'Switch value: {switch_value}')
		print(f"Nilai GPS: {gps_val}")
		
		# Send GPS data to ubidots
		payload = build_payload(VARIABLE_LABEL_GPS)
		print("[INFO] Attemping to send data")
		post_request(payload)
		print("[INFO] finished\n")
