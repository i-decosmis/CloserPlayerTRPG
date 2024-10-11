import zmq
import pygame
import sys
import time

# Inizializza Pygame
pygame.init()

# Configura il contesto ZeroMQ (inizialmente senza connessione)
context = zmq.Context()
socket = None
connected = False  # Stato della connessione
connection_message = "Non connesso"

# Imposta la finestra di Pygame
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Controllo Arduino da Tastiera")

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
input_box = pygame.Rect(50, 50, 300, 40)
ip_text = ''  # Testo inserito per l'IP
connect_button = pygame.Rect(150, 120, 120, 50)  # Pulsante di connessione
active_input = False  # Indica se il campo di input è attivo (focus)
cursor_visible = True  # Indica se il cursore lampeggiante è visibile

# Funzione per disegnare il pulsante
def draw_button(button_rect, text, active=False):
    """Disegna un pulsante in stile minimal."""
    # Colore diverso se il pulsante è attivo (hover)
    button_color = ACCENT_COLOR if active else LIGHT_GRAY
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)  # Pulsante con bordi arrotondati
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

# Funzione per disegnare l'interfaccia
def draw_interface(mouse_pos, cursor_visible):
    """Disegna l'interfaccia grafica."""
    screen.fill(WHITE)
    
    # Colore diverso per il bordo dell'input box quando è attivo (cliccato)
    input_color = ACTIVE_COLOR if active_input else LIGHT_GRAY
    pygame.draw.rect(screen, input_color, input_box, border_radius=10, width=2)  # Bordo arrotondato e più spesso se attivo

    # Disegna il testo all'interno del campo di input
    txt_surface = font.render(ip_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    # Aggiunge il cursore lampeggiante se il campo di input è attivo
    if active_input and cursor_visible:
        cursor_surface = font.render('|', True, BLACK)
        cursor_x = input_box.x + 10 + txt_surface.get_width() + 2  # Posizione del cursore alla fine del testo
        screen.blit(cursor_surface, (cursor_x, input_box.y + 5))

    # Messaggio di stato connessione
    status_surface = font.render(connection_message, True, DARK_GRAY if not connected else ACCENT_COLOR)
    screen.blit(status_surface, (20, 260))

    # Disegna il pulsante di connessione con effetto hover
    draw_button(connect_button, "Connetti", active=connect_button.collidepoint(mouse_pos))

    pygame.display.flip()

def send_command(command):
    """Invia un comando al server via ZeroMQ se connesso."""
    if connected:
        socket.send_string(command)
        response = socket.recv_string()

def try_connect(ip_address):
    """Prova a connettersi al server tramite l'indirizzo IP fornito."""
    global socket, connected, connection_message
    try:
        # Prova a creare una connessione
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{ip_address}:5556")
        connected = True
        connection_message = "Connesso"
    except Exception as e:
        connected = False
        connection_message = f"Errore: {str(e)}"

# Ciclo principale
running = True
speed = 6
blink_time = 0  # Timer per gestire il lampeggiamento del cursore

while running:
    mouse_pos = pygame.mouse.get_pos()  # Ottieni la posizione del mouse
    current_time = pygame.time.get_ticks()  # Tempo attuale in millisecondi
    
    # Lampeggiamento del cursore (ogni 500 ms)
    if current_time - blink_time > 500:
        cursor_visible = not cursor_visible
        blink_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        # Gestione degli eventi della tastiera e del mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Controlla se si clicca nel campo di input per l'IP
            if input_box.collidepoint(event.pos):
                active_input = True  # Attiva l'input se clicca nel box
            else:
                active_input = False  # Disattiva se clicca fuori dal box
            
            # Controlla se si clicca sul pulsante di connessione
            if connect_button.collidepoint(event.pos):
                if not connected:  # Permetti di connettersi solo se non già connesso
                    try_connect(ip_text)  # Prova a connettersi quando clicca sul pulsante

        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False  # Disattiva l'input al termine
                elif event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]  # Cancella l'ultimo carattere
                else:
                    ip_text += event.unicode  # Aggiunge il nuovo carattere

        # Controllo per i comandi del robot se connessi
        if connected and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                send_command("left")  # Gira a sinistra
            if event.key == pygame.K_RIGHT:
                send_command("right")  # Gira a destra
            if event.key == pygame.K_UP:
                speed = min(9, speed + 1)
                send_command(str(speed))  # Aumenta la velocità
            if event.key == pygame.K_DOWN:
                speed = max(4, speed - 1)
                send_command(str(speed))  # Diminuisce la velocità

        if connected and event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                send_command("S")  # Ferma il movimento

    # Aggiorna l'interfaccia grafica
    draw_interface(mouse_pos, cursor_visible)

# Chiudi il socket quando il programma termina
if socket:
    socket.close()
context.term()
