import zmq
import serial
import time
import threading
import pygame
import sys

# Funzione per leggere dalla porta seriale
def read_from_serial():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').rstrip()
            print(f"Messaggio da Arduino: {line}")

# Funzione per avviare il server ZMQ
def start_server(ip_address):
    global server_running, oldMessage

    try:
        # Crea il contesto ZeroMQ
        context = zmq.Context()

        # Crea un socket di tipo REQ/REP
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://{ip_address}:5556")

        print(f"Server in ascolto su {ip_address}:5556...")

        # Avvia un thread per leggere dalla porta seriale
        threading.Thread(target=read_from_serial, daemon=True).start()

        while server_running:
            try:
                message = socket.recv_string(flags=zmq.NOBLOCK)  # Non bloccare, controlla costantemente
                if message != oldMessage:
                    oldMessage = message
                    update_last_command(message)  # Aggiorna l'interfaccia
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
            except zmq.Again:  # Non ci sono messaggi disponibili
                pass

        arduino.close()
        socket.close()
        context.term()
        print("Server chiuso.")
    except Exception as e:
        print(f"Errore: {e}")

# Aggiorna l'ultimo comando ricevuto sull'interfaccia
def update_last_command(command):
    global last_command
    last_command = command

# Inizializza Pygame
pygame.init()

# Imposta la finestra di Pygame
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Server Controllo Arduino")

# Definisce alcuni colori in stile minimal
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
LIGHT_GRAY = (200, 200, 200)
GRAY = (170, 170, 170)
DARK_GRAY = (50, 50, 50)
ACCENT_COLOR = (0, 150, 136)  # Colore primario per i pulsanti (verde acqua)
ACTIVE_COLOR = (0, 200, 180)  # Colore del bordo quando il campo è attivo

# Imposta il font
font = pygame.font.Font(None, 36)

# Variabili per l'interfaccia
input_box = pygame.Rect(50, 50, 400, 40)
ip_text = ''  # Testo inserito per l'IP
start_button = pygame.Rect(150, 120, 200, 50)  # Pulsante per avviare il server
stop_button = pygame.Rect(150, 190, 200, 50)  # Pulsante per chiudere il server
active_input = False  # Indica se il campo di input è attivo (focus)
server_running = False  # Indica se il server è attivo
last_command = "Nulla"

# Funzione per disegnare il pulsante
def draw_button(button_rect, text, active=False):
    """Disegna un pulsante in stile minimal."""
    button_color = ACCENT_COLOR if active else LIGHT_GRAY
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

# Funzione per disegnare l'interfaccia
def draw_interface(mouse_pos):
    """Disegna l'interfaccia grafica."""
    screen.fill(WHITE)
    
    # Disegna l'input box per l'IP
    input_color = ACTIVE_COLOR if active_input else LIGHT_GRAY
    pygame.draw.rect(screen, input_color, input_box, border_radius=10, width=2)

    # Disegna il testo all'interno del campo di input
    txt_surface = font.render(ip_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    # Messaggio di stato
    status_text = "Server in esecuzione" if server_running else "Server non attivo"
    status_surface = font.render(status_text, True, DARK_GRAY)

    # Ottieni le dimensioni del testo e il rettangolo associato
    status_rect = status_surface.get_rect(center=(screen.get_width() // 2, 260))  # Centra orizzontalmente a y=260

    # Disegna il testo centrato
    screen.blit(status_surface, status_rect)

    # Ultimo comando ricevuto
    last_command_surface = font.render(f"Ultimo comando: {last_command}", True, DARK_GRAY)
    screen.blit(last_command_surface, (20, 350))

    # Disegna i pulsanti
    draw_button(start_button, "Avvia Server", active=start_button.collidepoint(mouse_pos))
    draw_button(stop_button, "Chiudi Server", active=stop_button.collidepoint(mouse_pos))

    pygame.display.flip()

# Ciclo principale
running = True
arduino = None
oldMessage = -1

while running:
    mouse_pos = pygame.mouse.get_pos()  # Ottieni la posizione del mouse

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            if server_running:
                server_running = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active_input = True
            else:
                active_input = False
            
            # Avvia il server
            if start_button.collidepoint(event.pos) and not server_running:
                arduino = serial.Serial('COM5', 9600, timeout=1)
                time.sleep(2)
                server_running = True
                threading.Thread(target=start_server, args=(ip_text,), daemon=True).start()
            
            # Chiudi il server
            if stop_button.collidepoint(event.pos) and server_running:
                server_running = False

        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False
                elif event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]
                else:
                    ip_text += event.unicode

    # Disegna l'interfaccia
    draw_interface(mouse_pos)

# Chiude il server e il contesto ZeroMQ alla fine
if arduino:
    arduino.close()
