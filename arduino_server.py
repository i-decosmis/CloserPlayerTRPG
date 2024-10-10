import zmq
import serial
import time
import threading

# Funzione per leggere dalla porta seriale
def read_from_serial():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').rstrip()
            print(f"Messaggio da Arduino: {line}")

# Imposta la connessione seriale con Arduino
arduino = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)

# Crea il contesto ZeroMQ
context = zmq.Context()

# Crea un socket di tipo REQ/REP
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:5556")

print("Server in ascolto per i comandi dei client...")

# Avvia un thread per leggere dalla porta seriale
threading.Thread(target=read_from_serial, daemon=True).start()

while True:
    message = socket.recv_string()
    print(f"Comando ricevuto: {message}")

    if message == "on":
        arduino.write(b'1')
        socket.send_string("Motorino acceso")
    elif message == "off":
        arduino.write(b'0')
        socket.send_string("Motorino spento")
    elif message == "left":
        arduino.write(b'L')
        socket.send_string("Motorino gira a sinistra")
    elif message == "right":
        arduino.write(b'R')
        socket.send_string("Motorino gira a destra")
    elif message.isdigit():  # Se riceviamo un numero, lo consideriamo come la velocità
        arduino.write(message.encode())  # Invia il numero come stringa ad Arduino
        socket.send_string(f"Velocità impostata a {int(message) * 25}")
    elif message == "exit":
        print("Chiusura del server...")
        break
    else:
        socket.send_string("Comando non riconosciuto")

arduino.close()
socket.close()
context.term()
print("Server chiuso.")
