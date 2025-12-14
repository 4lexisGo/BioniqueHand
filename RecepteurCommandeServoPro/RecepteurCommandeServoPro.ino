#include <Wire.h> // Inclure la bibliothèque Wire

const int a = 1;
const int b = 0;
const int c = 0;

byte Consigne1;
byte Consigne2;
byte Consigne3;
byte Intensitee1;
byte Intensitee2;
byte Intensitee3;

// Définir les broches pour les potentiomètres
const int potPin1 = A0; // Potentiomètre 1 (pour moteur 1) antihoraire diminue
const int potPin2 = A1; // Potentiomètre 2 (pour moteur 2) horaire diminue
const int potPin3 = A2; // Potentiomètre 2 (pour moteur 2) horaire diminue

// Définir les broches pour les entrées IN1 à IN4 du driver moteur
// Driver 1
const int motorPin1 = 2; // IN3 (moteur 1) sens anti horaire vu depuis l'arriere du moteur
const int motorPin2 = 3; // IN4 (moteur 1)

// Driver 2
const int motorPin3 = 4; // IN3 (moteur 2)
const int motorPin4 = 5; // IN4 (moteur 2) sens anti horaire vu depuis l'arriere du moteur
const int motorPin5 = 6; // IN1 (moteur 3) sens anti horaire vu depuis l'arriere du moteur
const int motorPin6 = 7; // IN2 (moteur 3)


int pV1;
int pV1Prev;
int pV1Global;
int G1Prev = 256*3; 
int Ecart1;
const int hyst1 = 50;
int pV1Target = 256*3;
int pV1TargetPrev;


int pV2;
int pV2Prev;
int Ecart2;
const int hyst2 = 50;
int pV2Target = 0;
int pV2TargetPrev;

int pV3;
int pV3Prev;
int Ecart3;
const int hyst3 = 50;
int pV3Target = 0;
int pV3TargetPrev;


void setup() {
  // Initialiser les broches du moteur en sortie
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  pinMode(motorPin3, OUTPUT);
  pinMode(motorPin4, OUTPUT);
  pinMode(motorPin5, OUTPUT);
  pinMode(motorPin6, OUTPUT);        

  // Initialiser la communication série pour le débogage
  Serial.begin(9600);
  delay(1000);        // Pause pour permettre à la connexion série de s'établir
}

void loop() {
  if (Serial.available() >= 6) {  // Attendre la réception de trois octets
    Consigne1 = Serial.read();
    Intensitee1 = Serial.read();
    Consigne2 = Serial.read();
    Intensitee2 = Serial.read();
    Consigne3 = Serial.read();
    Intensitee3 = Serial.read();
  }

  // Traitement potentiomètre 1
  pV1 = analogRead(potPin1); // Valeur du potentiomètre 1 (moteur 1)
  if (pV1 < 200 and pV1Prev > 900){
    Ecart1 = 0 + 1024 - pV1Prev + pV1;
  }
  else if (pV1Prev < 200 and pV1 > 900){
    Ecart1 = 0 - 1024 + pV1Prev - pV1;
  }
  else{
    Ecart1 = pV1 - pV1Prev;
  }
  pV1Global = (G1Prev + Ecart1) % (1024*4); // Rapport de réduction

  if (a == 1){
    Serial.print("Potentiomètre 1 : ");
    Serial.println(pV1);           // Envoyer la valeur lue au Moniteur Série
    Serial.print(", Global 1 : ");
    Serial.println(pV1);           // Envoyer la valeur lue au Moniteur Série
  }

  // Traitement potentiomètre 2
  pV2 = analogRead(potPin2); // Valeur du potentiomètre 1 (moteur 1)

  if (b == 1){
    Serial.print(", Potentiomètre 2 : ");
    Serial.println(pV2);           // Envoyer la valeur lue au Moniteur Série
  }

  // Traitement potentiomètre 3
  pV3 = analogRead(potPin3); // Valeur du potentiomètre 3 (moteur 3)

  if (c == 1){
    Serial.print(", Potentiomètre 3 : ");
    Serial.println(pV3);           // Envoyer la valeur lue au Moniteur Série
  }

  // Traitement Moteur 1
  if (Consigne1 == 1 ){
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
    delay(Intensitee1);
    digitalWrite(motorPin2, LOW);
  }
  else if (Consigne1 == 2){
    digitalWrite(motorPin2, LOW);
    digitalWrite(motorPin1, HIGH);
    delay(Intensitee1);
    digitalWrite(motorPin1, LOW);
  }
  else{
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
  }

  // Traitement Moteur 2
  if (Consigne2 == 1){
    digitalWrite(motorPin4, LOW);
    digitalWrite(motorPin3, HIGH);
    delay(Intensitee2);
    digitalWrite(motorPin3, LOW);
  }
  else if (Consigne2 == 2){
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, HIGH);
    delay(Intensitee2);
    digitalWrite(motorPin4, LOW);
  }
  else{
    digitalWrite(motorPin3, LOW);
    digitalWrite(motorPin4, LOW);
  }

  // Traitement Moteur 3
  if (Consigne3 == 1){
    digitalWrite(motorPin6, LOW);
    digitalWrite(motorPin5, HIGH);
    delay(Intensitee3);
    digitalWrite(motorPin5, LOW);
  }
  else if (Consigne3 == 2){
    digitalWrite(motorPin5, LOW);
    digitalWrite(motorPin6, HIGH);
    delay(Intensitee3);
    digitalWrite(motorPin6, LOW);
  }
  else{
    digitalWrite(motorPin5, LOW);
    digitalWrite(motorPin6, LOW);
  }

  // Sauvegarde données potentiomètres 1 et 2 et 3
  pV1Prev = pV1;
  G1Prev = pV1Global;
  pV1TargetPrev = pV1Target;

  pV2Prev = pV2;
  pV2TargetPrev = pV2Target;

  pV3Prev = pV3;
  pV3TargetPrev = pV3Target;

}
