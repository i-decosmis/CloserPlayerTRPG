import zmq
import pygame
import sys

# Inizializza Pygame
pygame.init()

# Configura il contesto ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:5556")

# Imposta la finestra di Pygame (facoltativa, poiché si usa solo per input)
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controllo Arduino da Tastiera")

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

        # Controllo degli input da tastiera
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                send_command("left")  # Gira a sinistra
            elif event.key == pygame.K_RIGHT:
                send_command("right")  # Gira a destra
            elif event.key == pygame.K_UP:
                send_command("on")  # Accende il motore
            elif event.key == pygame.K_DOWN:
                send_command("off")  # Spegne il motore
            elif event.key == pygame.K_4:
                send_command("4")  # Velocità 4
            elif event.key == pygame.K_5:
                send_command("5")  # Velocità 5
            elif event.key == pygame.K_6:
                send_command("6")  # Velocità 6
            elif event.key == pygame.K_7:
                send_command("7")  # Velocità 7
            elif event.key == pygame.K_8:
                send_command("8")  # Velocità 8
            elif event.key == pygame.K_9:
                send_command("9")  # Velocità 9

# Chiudi il socket
socket.close()
context.term()
