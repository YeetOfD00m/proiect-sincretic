# Importing Libraries 
import serial 
import time 

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
pinLED = 26
pinTemp = 33

def write_read(x): 
	arduino.write(bytes(x, 'utf-8')) 
	time.sleep(0.05) 
	data = arduino.readline() 
	return data 

def read_print_temp():
    temp = arduino.readline()
    print("Temperature: " + str(temp) + "/n")
    
while True: 
    read_print_temp()
