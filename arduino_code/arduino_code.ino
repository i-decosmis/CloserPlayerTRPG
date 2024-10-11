// This file is part of CloserPlayerTRPG.
//
// CloserPlayerTRPG is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// CloserPlayerTRPG is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

// Define the pins
int in1 = 2;  // Pin connected to IN1 of the L293D
int in2 = 3;  // Pin connected to IN2 of the L293D
int en = 5;   // Pin connected to EN of the L293D (PWM for speed control)
int speed = 200;  // Initial speed value (0-255)
char lastCommand = 'z';

void setup() {
  Serial.begin(9600);  // Set serial communication to 9600 baud rate
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(en, OUTPUT);

  // Set the motor in one direction with medium speed
  analogWrite(en, speed);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();  // Read the command

    if (command == 'L') {
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, LOW);  // Turn counter-clockwise
      digitalWrite(in2, HIGH);
    } else if (command == 'R') {
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, HIGH);  // Turn clockwise
      digitalWrite(in2, LOW);
    } else if (isdigit(command)) {  // Command to change speed (0-9)
      speed = (command - '0') * 25;  // Multiply to get a value between 0 and 255
      analogWrite(en, speed);
    } else if (command == 'S'){
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, LOW); 
      digitalWrite(in2, LOW);  // Stop the motor
    }
  }
}
