from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import serial
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = '' # cheie secreta pentru sesiuni, poate fi setata in .env sau lasata goala daca nu folositi sesiuni

# DEBUG EMAIL - Foloseste MailHog pentru testing local
DEBUG_EMAIL = os.getenv('DEBUG_EMAIL', 'False').lower() == 'true'

# configurare email pentru alerte inundatii
if DEBUG_EMAIL:
    # configurare MailHog (Development/Testing)
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'debug@example.com'
    print(" | INFO_EMAIL | DEBUG MODE - Using MailHog on localhost:1025")
    print(" | INFO_EMAIL | View emails at http://localhost:8025")
else:
    # configurare Gmail (Production)
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Conexiune seriala cu Arduino
arduino = None
ARDUINO_PORT = 'COM3'
ARDUINO_BAUD = 115200

# Variebilele globale pentru stocarea starii sistemului
current_temp = 0.0
led_status = False
messages = []
flood_events = []

def connect_arduino():
    global arduino
    try:
        arduino = serial.Serial(port=ARDUINO_PORT, baudrate=ARDUINO_BAUD, timeout=0.1)
        print(f" | INFO_CONNECT | Connected to Arduino on {ARDUINO_PORT}")
        return True
    except Exception as e:
        print(f" | ERROR | Failed to connect to Arduino: {e}")
        return False

def read_arduino_data():
    """Citeste date de la Arduino si actualizeaza starea sistemului"""
    
    global current_temp, led_status, flood_events
    
    if arduino is None or not arduino.is_open:
        print(f" | INFO_WARNING | Arduino not connected. Skipping data read.")
        return
    try:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            
            if line.startswith('TEMP:'):
                try:
                    current_temp = float(line.split(':')[1])
                except ValueError:
                    pass
            
            elif line == 'LED ON':
                led_status = True
            
            elif line == 'LED OFF':
                led_status = False
            
            elif line == 'FLOOD:DETECTED':
                event = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'message': 'Inundatie Detectata!'
                }
                flood_events.append(event)
                
                # Trimitere alerta prin email
                send_flood_alert_mail(event)
    
    except Exception as e:
        print(f" | ERROR | Error reading Arduino: {e}")

def send_command_to_arduino(cmd):
    if arduino is None or not arduino.is_open:
        return False
    try:
        arduino.write(bytes(cmd, 'utf-8'))
        time.sleep(0.05)
        return True
    except Exception as e:
        print(f" | ERROR | Error sending command: {e}")
        return False

def send_flood_alert_mail(event):
    try:
        recipient = os.getenv('FLOOD_ALERT_EMAIL', 'user@example.com')
        
        msg = Message(
            subject='Alertă INUNDAȚIE',
            recipients=[recipient],
            body=f"""
                ALERTĂ INUNDAȚIE!
                
                Timp: {event['timestamp']}
                Mesaj: {event['message']}
                
                Vă rugăm să verificați sistemul imediat.

                """
        )
        
        mail.send(msg)
        
        if DEBUG_EMAIL:
            print(f" | INFO_EMAIL | [MailHog] Flood alert sent - View at http://localhost:8025")
        else:
            print(f" | INFO_EMAIL | Flood alert email sent to {recipient}")
    except Exception as e:
        print(f" | ERROR | Failed to send flood alert: {e}")

@app.before_request
def before_request():
    """Citeste datele de la Arduino înainte de fiecare cerere pentru a menține starea actualizată"""

    read_arduino_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    read_arduino_data()
    return jsonify({
        'temperature': current_temp,
        'led_status': led_status,
        'messages': messages[-10:],  # Ultimele 10 mesaje
        'flood_events': flood_events[-10:]  # Ultimele 10 evenimente
    })

@app.route('/api/led/on', methods=['POST'])
def turn_led_on():
    if send_command_to_arduino('A'):
        global led_status
        led_status = True
        messages.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': 'LED pornit din interfață web',
            'type': 'LED_ON'
        })
        return jsonify({'success': True, 'status': 'LED ON'})
    return jsonify({'success': False, 'error': 'Failed to send command'}), 500

@app.route('/api/led/off', methods=['POST'])
def turn_led_off():
    if send_command_to_arduino('S'):
        global led_status
        led_status = False
        messages.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': 'LED stins din interfață web',
            'type': 'LED_OFF'
        })
        return jsonify({'success': True, 'status': 'LED OFF'})
    return jsonify({'success': False, 'error': 'Failed to send command'}), 500

@app.route('/api/message/send', methods=['POST'])
def send_message_to_arduino():

    data = request.json
    msg = data.get('message', '')
    
    if not msg:
        return jsonify({'success': False, 'error': 'Empty message'}), 400
    
    if len(msg) > 60:
        return jsonify({'success': False, 'error': 'Message too long (max 60 chars)'}), 400
    
    if send_command_to_arduino(msg):
        messages.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': msg,
            'type': 'USER_MESSAGE'
        })
        # Keep only last 10
        if len(messages) > 10:
            messages.pop(0)
        
        return jsonify({'success': True, 'message': 'Message sent'})
    
    return jsonify({'success': False, 'error': 'Failed to send message'}), 500

@app.route('/api/flood/delete/<int:index>', methods=['DELETE'])
def delete_flood_event(index):
    global flood_events
    if 0 <= index < len(flood_events):
        flood_events.pop(index)
        return jsonify({'success': True, 'message': 'Event deleted'})
    return jsonify({'success': False, 'error': 'Invalid index'}), 400

@app.route('/api/flood/clear', methods=['POST'])
def clear_flood_events():
    global flood_events
    flood_events = []
    send_command_to_arduino('X')  # Trimit comanda de curatare a evenimentelor de inundatie catre Arduino
    return jsonify({'success': True, 'message': 'All flood events cleared'})

@app.route('/api/messages/clear', methods=['POST'])
def clear_messages():
    global messages
    messages = []
    send_command_to_arduino('C')  # Trimit comanda de curatare a mesajelor catre Arduino
    return jsonify({'success': True, 'message': 'All messages cleared'})

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    read_arduino_data()
    return jsonify({'temperature': current_temp})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    if not connect_arduino():  # Daca conexiunea cu Arduino esueaza, continuam fara ea
        print(" | INFO_WARNING | Continuing without Arduino connection. Some features may not work.")
      
    app.run(debug=True, host='0.0.0.0', port=5000) # Ruleaza aplicatia Flask
