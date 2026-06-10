// PSN Proiect Sincretic Anul 3 - Control Panel

// Tema 1: LED Control
// Tema 4: Citire temperatura
// Tema 3: Detectare inundatii

#include <EEPROM.h>  // Standard EEPROM library

// Setari 
const int pinLED = 26;
const int pinTemp = 33;
const int pinFloodSensor = 32;
static bool floodAlerted = false;

// adrese EEPROM (fiecare mesaj sau eveniment ocupa 64 bytes, max 10 mesaje/evenimente)
const int MSG_START_ADDR = 0;      // Mesaje: 0-639 (10 messages x 64 bytes)
const int FLOOD_START_ADDR = 640;  // Inundatii: 640-1279 (10 events x 64 bytes)
const int MSG_COUNT_ADDR = 1280;   // Contor mesaje (1 byte)
const int FLOOD_COUNT_ADDR = 1281; // Contor evenimente inundatii (1 byte)
const int MSG_INDEX_ADDR = 1282;   // Index mesaj curent (1 byte)
const int FLOOD_INDEX_ADDR = 1283; // Index inundatie curenta (1 byte)

// Buffers
char messageBuffer[64];
byte messageCount = 0;
byte messageIndex = 0;
byte floodCount = 0;
byte floodIndex = 0;
unsigned long lastTempReadTime = 0;
unsigned long lastFloodAlertTime = 0;

void setup() {
  Serial.begin(115200);
  
  // Initializare pini
  pinMode(pinLED, OUTPUT);
  digitalWrite(pinLED, LOW);
  pinMode(pinFloodSensor, INPUT);
  pinMode(pinTemp, INPUT);

  messageCount = EEPROM.read(MSG_COUNT_ADDR);
  messageIndex = EEPROM.read(MSG_INDEX_ADDR);
  floodCount = EEPROM.read(FLOOD_COUNT_ADDR);
  floodIndex = EEPROM.read(FLOOD_INDEX_ADDR);
  
  if (messageCount > 10) messageCount = 10;
  if (floodCount > 10) floodCount = 10;
  
  Serial.println(" | INFO | PSN Proiect Sincretic Anul 3 Initialized");
  Serial.println(" | INFO | Commands: 'A' (LED ON), 'S' (LED OFF), 'T' (Read Temp), 'M' (Show Messages), 'F' (Show Floods)");
}

void loop() {
  if (millis() - lastTempReadTime > 1000) {
    readTemperature();
    lastTempReadTime = millis();
  }
  
  if (millis() - lastFloodAlertTime > 1000) {
    checkFloodSensor();
  }
  
  // Menegeriază comenzile primite prin serial
  if (Serial.available()) {
    char command = Serial.read();
    handleCommand(command);
  }
}

void readTemperature() {
  int analog = analogRead(pinTemp);
  float voltage = 5.0 * analog / 1023.0;
  float temperature = voltage * 25.0; 
  
  Serial.print("TEMP:");
  Serial.println(temperature);
}

void handleCommand(char cmd) {
  cmd = toupper(cmd);
  
  switch(cmd) {
    case 'A': // Porneste LED
      digitalWrite(pinLED, HIGH);
      storeMessage("LED:ON");
      Serial.println(" | INFO | LED ON");
      break;
      
    case 'S': // Opreste LED
      digitalWrite(pinLED, LOW);
      storeMessage("LED:OFF");
      Serial.println(" | INFO | LED OFF");
      break;
      
    case 'T': // Citeste temperatura
      readTemperature();
      break;
      
    case 'M': // Arata toate mesajele stocate
      showMessages();
      break;
      
    case 'F': // Arata toate evenimentele de inundatie stocate
      showFloods();
      break;
      
    case 'C': // Da clear la toate mesajele
      clearMessages();
      Serial.println(" | INFO | Messages cleared");
      break;
      
    case 'X': // Clear all floods
      clearFloods();
      Serial.println(" | INFO | Floods cleared");
      break;
      
    default:
      Serial.print(" | ERROR | Unknown command: ");
      Serial.println(cmd);
  }
}

void storeMessage(const char* msg) {

  int addr = MSG_START_ADDR + (messageIndex * 64); // Calculam adresa pentru acest mesaj

  for (int i = 0; i < 64; i++) {
    EEPROM.write(addr + i, 0);
  }
  
  for (int i = 0; i < 63 && msg[i] != '\0'; i++) {
    EEPROM.write(addr + i, msg[i]);
  }
  
  // Dam update la index si contor
  messageIndex = (messageIndex + 1) % 10;
  if (messageCount < 10) messageCount++;
  
  EEPROM.write(MSG_INDEX_ADDR, messageIndex);
  EEPROM.write(MSG_COUNT_ADDR, messageCount);
}

void storeFloodEvent(const char* msg) {
  int addr = FLOOD_START_ADDR + (floodIndex * 64); // Calculam adresa pentru acest eveniment de inundatie
  
  for (int i = 0; i < 64; i++) {
    EEPROM.write(addr + i, 0);
  }
  
  for (int i = 0; i < 63 && msg[i] != '\0'; i++) {
    EEPROM.write(addr + i, msg[i]);
  }
  
  // Dam update la index si contor
  floodIndex = (floodIndex + 1) % 10;
  if (floodCount < 10) floodCount++;
  
  EEPROM.write(FLOOD_INDEX_ADDR, floodIndex);
  EEPROM.write(FLOOD_COUNT_ADDR, floodCount);
}

void showMessages() {
  Serial.println(" | Stored Messages |");
  for (int i = 0; i < messageCount; i++) {
    int addr = MSG_START_ADDR + (i * 64);
    Serial.print(" | INFO | Msg ");
    Serial.print(i + 1);
    Serial.print(": ");
    for (int j = 0; j < 64; j++) {
      char c = EEPROM.read(addr + j);
      if (c == 0) break;
      Serial.print(c);
    }
    Serial.println();
  }
  Serial.println("-------------------");
}

void showFloods() {
  Serial.println(" | Flood Events |");
  for (int i = 0; i < floodCount; i++) {
    int addr = FLOOD_START_ADDR + (i * 64);
    Serial.print(" | INFO | Event ");
    Serial.print(i + 1);
    Serial.print(": ");
    for (int j = 0; j < 64; j++) {
      char c = EEPROM.read(addr + j);
      if (c == 0) break;
      Serial.print(c);
    }
    Serial.println();
  }
  Serial.println("-------------------");
}

void clearMessages() {
  for (int i = MSG_START_ADDR; i < FLOOD_START_ADDR; i++) {
    EEPROM.write(i, 0);
  }
  messageCount = 0;
  messageIndex = 0;
  EEPROM.write(MSG_COUNT_ADDR, 0);
  EEPROM.write(MSG_INDEX_ADDR, 0);
}

void clearFloods() {
  for (int i = FLOOD_START_ADDR; i < MSG_COUNT_ADDR; i++) {
    EEPROM.write(i, 0);
  }
  floodCount = 0;
  floodIndex = 0;
  EEPROM.write(FLOOD_COUNT_ADDR, 0);
  EEPROM.write(FLOOD_INDEX_ADDR, 0);
}

void checkFloodSensor() {
  // Citeste starea senzorului de inundatie
  int floodState = digitalRead(pinFloodSensor);
  
  if (floodState == HIGH) { // Inundatie detectata
    lastFloodAlertTime = millis();
    if(!floodAlerted) {
      Serial.println("FLOOD:DETECTED");
      storeFloodEvent(" | FLOOD | DETECTED");
      floodAlerted = true;
    }
  } else {
    //Serial.println("FLOOD:FALSE");
    floodAlerted = false;
  }
}
