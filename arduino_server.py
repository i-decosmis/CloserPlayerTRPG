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
oldMessage = -1

while True:
    message = socket.recv_string()
    if message != oldMessage:
        oldMessage = message
        if message.isnumeric():
            print(f"Velocita' aggiornata a: {message}")
        else:
            print(f"Comando ricevuto: {message}")

    if message == "left":
        arduino.write(b'L')
    elif message == "right":
        arduino.write(b'R')
    elif message.isdigit():  # Se riceviamo un numero, lo consideriamo come la velocità
        arduino.write(message.encode())  # Invia il numero come stringa ad Arduino
    elif message == "S":
        arduino.write(b'S')
    elif message == "exit":
        break
    else:
        socket.send_string("Comando non riconosciuto")
    socket.send_string(f"Comando '{message}' ricevuto")

arduino.close()
socket.close()
context.term()
print("Server chiuso.")
