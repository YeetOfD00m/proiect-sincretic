# Importing Libraries 
import serial 
import time 
import send_email

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=.1) 
pinLED = 26
pinTemp = 33

global current_temp

# scriere in serial - 'A' aprinde ledul, 'S' il stinge
def write_read(x): 
	arduino.write(bytes(x, 'utf-8'))  

# trimitere alarma inundatie prin email
def send_alarm():
	#construire data alarma
	current_datetime = time.localtime()
	days = ["Luni","Marti","Miercuri","Joi","Vineri","Sambata","Duminica"]
	current_date = days[current_datetime.tm_wday] + ", " + str(current_datetime.tm_mday) + "." + str(current_datetime.tm_mon)
		
	current_time = str(current_datetime.tm_hour) + ":" + str(current_datetime.tm_min) + ":" + str(current_datetime.tm_sec)

	# trimite email
	email_alert = send_email.build_email("Alarma inundatie " + current_date + " la ora " + current_time + " !")
	send_email.send(email_alert, debug=False)

def read_serial():
	# citire mesaj, decodare si impartire cuv cheie
	# val posibile: temp f, inundatie temp f (in caz de alarma)
	message = arduino.readline().decode("utf-8").split(" ")

	# rutina alarma inundatie
	if message[0] == "inundatie":
		send_alarm()
		time.sleep(2) # delay ca sa nu spamam accidental - tre inlocuit cu cv but as of now it works
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
