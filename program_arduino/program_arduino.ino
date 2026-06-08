#include <EEPROM.h>

char x; 

int pinLED = 26;
int pinTemp = 33;
int pinButton = 32;
float temp;
int eeprom_pos = 0;

void write_eeprom(int value) 
{
	EEPROM.write(eeprom_pos, value); // ar trebui EEPROM.update normal da na csf
	if (eeprom_pos == 10) { eeprom_pos = 0; }
	else { eeprom_pos += 1; }
}
	

void setup() { 
	// pins
	pinMode(pinLED, OUTPUT);
	pinMode(pinTemp, INPUT);
	pinMode(pinButton, INPUT);
	
	// serial
	Serial.begin(115200); 
	Serial.setTimeout(1); 

	digitalWrite(pinLED, LOW);
} 

void loop() { 
	//while (!Serial.available()); 
	x = Serial.read();
	if (x == 'A') 
	{
		digitalWrite(pinLED, HIGH);
	} 
	else if (x == 'S')
	{
		digitalWrite(pinLED, LOW);
	}
	
	int valADC = analogRead(pinTemp);       // Citim valoarea analogica (0-1023)
  float tensiune = valADC * (5.0 / 1023); // Convertim in Volti (0-5V)
	temp = tensiune * 100; // 10mV = 1°C => 1V = 100°C
	if (digitalRead(pinButton) == HIGH) 
	{
	Serial.print("inundatie "); 
	}
	Serial.print("temp ");
	Serial.println(temp); 
	delay(100);
} 

