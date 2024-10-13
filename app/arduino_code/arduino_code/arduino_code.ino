int IN1 = 7;
int IN2 = 8;
int IN3 = 12;
int IN4 = 13;
int speed = 1185;

// Sequenza di passi per il motore passo-passo
int steps[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

char lastCommand = 'z';
bool isRunning = false;  // Variabile per tenere traccia se il motore è in esecuzione
char currentDirection = 'R';  // Direzione corrente del motore ('R' o 'L')

void setup() {
  Serial.begin(9600);  // Set serial communication to 9600 baud rate
  // Imposta i pin come uscite
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {
  // Controlla se ci sono nuovi comandi dalla seriale
  if (Serial.available() > 0) {
    char command = Serial.read();  // Legge il comando

    // Se il comando è 'R', imposta il motore per girare a destra
    if (command == 'R') {
      if (lastCommand != command) {
        lastCommand = command;
        currentDirection = 'R';
        isRunning = true;  // Attiva il motore
      }
    }
    // Se il comando è 'L', imposta il motore per girare a sinistra
    else if (command == 'L') {
      if (lastCommand != command) {
        lastCommand = command;
        currentDirection = 'L';
        isRunning = true;  // Attiva il motore
      }
    }
    // Se il comando è un numero (1-9), cambia la velocità
    else if (isdigit(command)) {  
      speed = 723 + ((command - '0') * 77);
    }
    // Se il comando è 'S', ferma il motore
    else if (command == 'S') {
      isRunning = false;  // Ferma il motore
      lastCommand = command;
    }
  }

  // Se il motore è attivo, esegui il movimento nella direzione corrente
  if (isRunning) {
    if (currentDirection == 'R') {
      right();
    } else if (currentDirection == 'L') {
      left();
    }
  }
}

// Funzione per muovere il motore in avanti
void right() {
  for (int j = 0; j < 8; j++) {
    digitalWrite(IN1, steps[j][0]);
    digitalWrite(IN2, steps[j][1]);
    digitalWrite(IN3, steps[j][2]);
    digitalWrite(IN4, steps[j][3]);
    delayMicroseconds(speed);  // Imposta il ritardo tra i passi
  }
}

// Funzione per muovere il motore all'indietro
void left() {
  for (int j = 7; j >= 0; j--) {
    digitalWrite(IN1, steps[j][0]);
    digitalWrite(IN2, steps[j][1]);
    digitalWrite(IN3, steps[j][2]);
    digitalWrite(IN4, steps[j][3]);
    delayMicroseconds(speed);  // Imposta il ritardo tra i passi
  }
}
