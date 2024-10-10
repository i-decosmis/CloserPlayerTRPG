import zmq
import pygame
import sys
import time

# Inizializza Pygame
pygame.init()
print("Finito")

# Configura il contesto ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5556")

# Imposta la finestra di Pygame (facoltativa, poiché si usa solo per input)
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controllo Arduino da Tastiera")

def increase_speed(speed):
    if speed < 9:
        speed += 1
    return speed

def decrease_speed(speed):
    if speed > 4:
        speed -= 1
    return speed

def send_command(command):
    """Invia un comando al server via ZeroMQ"""
    socket.send_string(command)
    response = socket.recv_string()
# Ciclo principale
running = True
speed = 6
stop = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

    # Controllo evento KEYDOWN per quando si preme un tasto
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                send_command("left")  # Gira a sinistra
            if event.key == pygame.K_RIGHT:
                send_command("right")  # Gira a destra
            if event.key == pygame.K_UP:
                speed = increase_speed(speed)
                send_command(str(speed))  # Accende il motore
            if event.key == pygame.K_DOWN:
                speed = decrease_speed(speed)
                send_command(str(speed))  # Diminuisce la velocità

        # Controllo evento KEYUP per quando si rilascia un tasto
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                send_command("S")  # Spegne il motore

# Chiudi il socket
socket.close()
context.term()
