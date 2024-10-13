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
import pygame
import sys

# Initialize Pygame
pygame.init()

# Configure the ZeroMQ context (initially without connection)
context = zmq.Context()
socket = None
connected = False  # Connection status
connection_message = "Not connected"
last_command = ""  # Variable to store the last executed command

# Set up the Pygame window
screen = pygame.display.set_mode((400, 300))  # Window without borders
pygame.display.set_caption("Arduino Control via Keyboard")

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
input_box = pygame.Rect(50, 50, 300, 40)
ip_text = ''  # Text entered for the IP
connect_button = pygame.Rect(150, 120, 120, 50)  # Connection button
active_input = False  # Indicates whether the input field is active (focus)
cursor_visible = True  # Indicates whether the blinking cursor is visible

# Function to draw the button
def draw_button(button_rect, text, active=False):
    """Draws a button in minimal style."""
    button_color = ACCENT_COLOR if active else LIGHT_GRAY
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)  # Button with rounded corners
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

# Function to draw the interface
def draw_interface(mouse_pos):
    """Draws the graphical interface."""
    screen.fill(WHITE)

    if connected:  # If connected, only show the last command
        last_command_surface = font.render(f"{last_command}", True, BLACK)
        screen.blit(last_command_surface, (10, 13))
    else:
        # Different color for the input box border when active
        input_color = ACTIVE_COLOR if active_input else LIGHT_GRAY
        pygame.draw.rect(screen, input_color, input_box, border_radius=10, width=2)  # Rounded border and thicker if active

        # Draw the text inside the input field
        txt_surface = font.render(ip_text, True, BLACK)
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

        # Adds the blinking cursor if the input field is active
        if active_input and cursor_visible:
            cursor_surface = font.render('|', True, BLACK)
            cursor_x = input_box.x + 10 + txt_surface.get_width() + 2  # Position of the cursor at the end of the text
            screen.blit(cursor_surface, (cursor_x, input_box.y + 5))

        # Connection status message
        status_surface = font.render(connection_message, True, DARK_GRAY if not connected else ACCENT_COLOR)
        screen.blit(status_surface, (20, 260))

        # Draw the connection button with hover effect
        draw_button(connect_button, "Connect", active=connect_button.collidepoint(mouse_pos))

    pygame.display.flip()

def send_command(command):
    """Sends a command to the server via ZeroMQ if connected.""" 
    if connected:
        socket.send_string(command)
        response = socket.recv_string()
        return response

def try_connect(ip_address):
    """Attempts to connect to the server via the provided IP address.""" 
    global socket, connected, connection_message, last_command
    try:
        # Try to create a connection
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{ip_address}")
        connected = True
        connection_message = "Connected"
        pygame.display.set_mode((200, 50))  # Resize the window
    except Exception as e:
        connected = False
        connection_message = f"Error: {str(e)}"

# Main loop
running = True
speed = 6
blink_time = 0  # Timer to manage cursor blinking

while running:
    mouse_pos = pygame.mouse.get_pos()  # Get mouse position
    current_time = pygame.time.get_ticks()  # Current time in milliseconds
    
    # Cursor blinking (every 500 ms)
    if current_time - blink_time > 500:
        cursor_visible = not cursor_visible
        blink_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        
        # Handle keyboard and mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked in the input field for the IP
            if input_box.collidepoint(event.pos):
                active_input = True  # Activate input if clicked in the box
            else:
                active_input = False  # Deactivate if clicked outside the box
            
            # Check if clicked on the connection button
            if connect_button.collidepoint(event.pos) and not connected:
                try_connect(ip_text)  # Try to connect when clicking the button

        if event.type == pygame.KEYDOWN:
            if active_input:
                if event.key == pygame.K_RETURN:
                    active_input = False  # Deactivate input at end
                elif event.key == pygame.K_BACKSPACE:
                    ip_text = ip_text[:-1]  # Delete the last character
                else:
                    ip_text += event.unicode  # Add the new character

        # Check for robot commands if connected
        if connected and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                speed = min(9, speed + 1)
                last_command = f"Speed: {speed}"  # Store the last command
                send_command(str(speed))  # Increase speed
            if event.key == pygame.K_DOWN:
                speed = max(1, speed - 1)
                last_command = f"Speed: {speed}"  # Store the last command
                send_command(str(speed))  # Decrease speed
            if event.key == pygame.K_RIGHT:
                last_command = "Right"  # Store the last command
                send_command("right")  # Turn right
            if event.key == pygame.K_LEFT:
                last_command = "Left"  # Store the last command
                send_command("left")  # Turn left

        if connected and event.type == pygame.KEYUP:
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]:
                last_command = "Stop"  # Store the last command
                send_command("S")  # Stop movement

    # Update the graphical interface
    draw_interface(mouse_pos)

# Close the socket when the program terminates
if socket:
    socket.close()
context.term()
