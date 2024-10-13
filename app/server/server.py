# This file is part of CloserPlayerTRPG.
#
# CloserPlayerTRPG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CloserPlayerTRPG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import zmq
import serial
import time
import threading
import pygame
import sys
from serial.tools import list_ports


# Function to read from the serial port
def read_from_serial():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').rstrip()
            print(f"Message from Arduino: {line}")

# Function to list available serial ports
def get_serial_ports():
    ports = list_ports.comports()
    return [port.device for port in ports]

serial_ports = get_serial_ports()  # List of available ports
selected_port = None  # User-selected port
show_ports = False  # Flag to show/hide the port selection menu


# Function to start the ZMQ server
def start_server(ip_address):
    global server_running, oldMessage

    try:
        # Create the ZeroMQ context
        context = zmq.Context()

        # Create a REQ/REP type socket
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://{ip_address}")

        print(f"Server listening on {ip_address}...")

        # Start a thread to read from the serial port
        threading.Thread(target=read_from_serial, daemon=True).start()

        while server_running:
            try:
                message = socket.recv_string(flags=zmq.NOBLOCK)  # Non-blocking, constantly checking
                if message != oldMessage:
                    oldMessage = message
                    update_last_command(message)  # Update the interface
                    if message.isnumeric():
                        print(f"Speed updated to: {message}")
                    else:
                        print(f"Command received: {message}")

                if message == "right":
                    arduino.write(b'R')
                elif message == "left":
                    arduino.write(b'L')
                elif message.isdigit():  # If we receive a number, we consider it as speed
                    arduino.write(message.encode())  # Send the number as a string to Arduino
                elif message == "S":
                    arduino.write(b'S')
                elif message == "exit":
                    break
                else:
                    socket.send_string("Unrecognized command")
                socket.send_string(f"Command '{message}' received")
            except zmq.Again:  # No messages available
                pass

        arduino.close()
        socket.close()
        context.term()
        print("Server closed.")
    except Exception as e:
        print(f"Error: {e}")

# Update the last received command on the interface
def update_last_command(command):
    global last_command
    last_command = command

# Initialize Pygame
pygame.init()

# Set up the Pygame window
screen = pygame.display.set_mode((500, 400))
pygame.display.set_caption("Arduino Control Server")

# Define some minimal style colors
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
LIGHT_GRAY = (200, 200, 200)
GRAY = (170, 170, 170)
DARK_GRAY = (50, 50, 50)
ACCENT_COLOR = (0, 150, 136)  # Primary color for buttons (teal)
ACTIVE_COLOR = (0, 200, 180)  # Border color when the field is active

# Set the font
font = pygame.font.Font(None, 36)

# Variables for the interface
input_box = pygame.Rect(50, 50, 400, 40)
ip_text = ''  # Text entered for the IP
start_button = pygame.Rect(150, 120, 200, 50)  # Button to start the server
stop_button = pygame.Rect(150, 190, 200, 50)  # Button to close the server
active_input = False  # Indicates whether the input field is active (focus)
server_running = False  # Indicates whether the server is active
last_command = "None"

# Function to draw the button
def draw_button(button_rect, text, active=False):
    """Draws a button in minimal style."""
    button_color = LIGHT_GRAY if active else ACCENT_COLOR
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

# Function to draw the serial port selection menu
def draw_serial_port_menu():
    global show_ports, selected_port

    if selected_port:
        # If a port is selected, show the selected port and disable further selection
        selected_port_surface = font.render(f"{selected_port}", True, DARK_GRAY)
        screen.blit(selected_port_surface, (340, 10))
    else:
        # If no port is selected, show the "Select Port" button
        select_port_button = pygame.Rect(340, 10, 150, 30)
        pygame.draw.rect(screen, ACCENT_COLOR, select_port_button, border_radius=5)
        select_port_surface = font.render("Select Port", True, WHITE)
        screen.blit(select_port_surface, (select_port_button.x + 10, select_port_button.y + 5))

        # Toggle the port menu when the button is clicked
        if pygame.mouse.get_pressed()[0] and select_port_button.collidepoint(pygame.mouse.get_pos()):
            show_ports = True

    if show_ports and not selected_port:
        # Display the available ports as a list
        for i, port in enumerate(serial_ports):
            port_rect = pygame.Rect(340, 50 + i * 40, 150, 30)
            pygame.draw.rect(screen, LIGHT_GRAY, port_rect, border_radius=5)
            port_surface = font.render(port, True, BLACK)
            screen.blit(port_surface, (port_rect.x + 10, port_rect.y + 5))

            # Check if a port was clicked
            if pygame.mouse.get_pressed()[0] and port_rect.collidepoint(pygame.mouse.get_pos()):
                selected_port = port  # Store the selected port
                show_ports = False  # Hide the menu after selection



# Function to draw the interface
def draw_interface(mouse_pos):
    """Draws the graphical interface."""
    screen.fill(WHITE)
    
    # Draw the input box for the IP
    input_color = ACTIVE_COLOR if active_input else LIGHT_GRAY
    pygame.draw.rect(screen, input_color, input_box, border_radius=10, width=2)

    # Draw the text inside the input field
    txt_surface = font.render(ip_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    # Status message
    status_text = "Server running" if server_running else "Server not active"
    status_surface = font.render(status_text, True, DARK_GRAY)
    status_rect = status_surface.get_rect(center=(screen.get_width() // 2, 260))  # Center horizontally at y=260
    screen.blit(status_surface, status_rect)

    # Last command received
    last_command_surface = font.render(f"Last command: {last_command}", True, DARK_GRAY)
    screen.blit(last_command_surface, (20, 350))

    # Draw the buttons
    draw_button(start_button, "Start Server", active=start_button.collidepoint(mouse_pos))

    # Draw the serial port selection menu
    draw_serial_port_menu()

    pygame.display.flip()


# Main loop
running = True
arduino = None
oldMessage = -1

while running:
    mouse_pos = pygame.mouse.get_pos()  # Get mouse position

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

            # Start the server only if a port is selected
            if start_button.collidepoint(event.pos) and not server_running and selected_port:
                arduino = serial.Serial(selected_port, 9600, timeout=1)
                time.sleep(2)
                server_running = True
                threading.Thread(target=start_server, args=(ip_text,), daemon=True).start()

        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False
                elif event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]
                else:
                    ip_text += event.unicode

    # Draw the interface
    draw_interface(mouse_pos)

# Close the server and the ZeroMQ context at the end
if arduino:
    arduino.close()
