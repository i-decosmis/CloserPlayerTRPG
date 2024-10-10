import zmq
import pygame
import sys

# Inizializza Pygame
pygame.init()

# Configura ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5556")

# Inizializza il controller
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Controller rilevato: {joystick.get_name()}")
else:
    print("Nessun controller trovato")
    sys.exit()

def send_command(command):
    """Invia un comando al server via ZeroMQ"""
    socket.send_string(command)
    response = socket.recv_string()
    print(f"Risposta dal server: {response}")

# Ciclo principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(0):  # Es: tasto A
                send_command("on")  # Accende il motore
            elif joystick.get_button(1):  # Es: tasto B
                send_command("off")  # Spegne il motore
            elif joystick.get_button(2):  # Es: tasto X
                send_command("left")  # Gira a sinistra
            elif joystick.get_button(3):  # Es: tasto Y
                send_command("right")  # Gira a destra

        # Controlla gli stick per la velocità
        if event.type == pygame.JOYAXISMOTION:
            axis_value = joystick.get_axis(1)  # Es: asse verticale
            speed = int((axis_value + 1) / 2 * 9)  # Mappa il valore (-1,1) a (0,9)
            send_command(str(speed))

# Chiudi il socket
socket.close()
context.term()
