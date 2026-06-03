# Importing Libraries 
import serial 
import time 
import send_email

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
pinLED = 26
pinTemp = 33

global current_temp

def write_read(x): 
	arduino.write(bytes(x, 'utf-8'))  
	#data = arduino.readline() 
	#return data 

def read_serial():
	# citire mesaj, decodare si impartire cuv cheie
	# val posibile: temp f, inundatie temp f (in caz de alarma)
	message = arduino.readline().decode("utf-8").split(" ")

	# rutina alarma inundatie
	if message[0] == "inundatie":
		email_alert = send_email.build_email("Alarma inundatie la " + str(time.localtime()) + " !")
		send_email.send(email_alert, debug=False)
		time.sleep(2)
		message.remove("inundatie")
	if message[0] == "temp":
		current_temp = float(message[1])
		print("Temperature: " + str(current_temp))
		
	
	#time.sleep(0.2)

while True: 
	read_serial()
	#write_read('A')
	time.sleep(0.2)
	#write_read('S')
