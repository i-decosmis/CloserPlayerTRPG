// Definisci i pin
int in1 = 2;  // Pin collegato a IN1 del L293D
int in2 = 3;  // Pin collegato a IN2 del L293D
int en = 5;   // Pin collegato a EN del L293D (PWM per il controllo della velocità)
int speed = 200;  // Valore di velocità iniziale (0-255)
char lastCommand = 'z';

void setup() {
  Serial.begin(9600);  // Imposta la comunicazione seriale a 9600 baud rate
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(en, OUTPUT);

  // Imposta il motore in una direzione con velocità media
  analogWrite(en, speed);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);

}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();  // Leggi il comando

    if (command == 'L') {
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, LOW);  // Gira in senso antiorario
      digitalWrite(in2, HIGH);
    } else if (command == 'R') {
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, HIGH);  // Gira in senso orario
      digitalWrite(in2, LOW);
    } else if (isdigit(command)) {  // Comando per modificare la velocità (0-9)
      speed = (command - '0') * 25;  // Moltiplichiamo per ottenere un valore tra 0 e 255
      analogWrite(en, speed);
    } else if (command == 'S'){
      if (lastCommand != command) {
        lastCommand = command;
      }
      digitalWrite(in1, LOW); 
      digitalWrite(in2, LOW);
    }
  }
}
