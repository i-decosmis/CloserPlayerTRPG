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

# Function to read from the serial port
def read_from_serial():
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').rstrip()
            print(f"Message from Arduino: {line}")

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

                if message == "up":
                    arduino.write(b'U')
                elif message == "down":
                    arduino.write(b'D')
                elif message == "right":
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
    button_color = ACCENT_COLOR if active else LIGHT_GRAY
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

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

    # Get the size of the text and the associated rectangle
    status_rect = status_surface.get_rect(center=(screen.get_width() // 2, 260))  # Center horizontally at y=260

    # Draw the centered text
    screen.blit(status_surface, status_rect)

    # Last command received
    last_command_surface = font.render(f"Last command: {last_command}", True, DARK_GRAY)
    screen.blit(last_command_surface, (20, 350))

    # Draw the buttons
    draw_button(start_button, "Start Server", active=start_button.collidepoint(mouse_pos))
    draw_button(stop_button, "Stop Server", active=stop_button.collidepoint(mouse_pos))

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
            
            # Start the server
            if start_button.collidepoint(event.pos) and not server_running:
                arduino = serial.Serial('COM5', 9600, timeout=1)
                time.sleep(2)
                server_running = True
                threading.Thread(target=start_server, args=(ip_text,), daemon=True).start()
            
            # Close the server
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

    # Draw the interface
    draw_interface(mouse_pos)

# Close the server and the ZeroMQ context at the end
if arduino:
    arduino.close()
