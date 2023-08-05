//int led = 8;
//void setup() {
//  pinMode(led,OUTPUT);
//  Serial.begin(9600);
//}
//void loop() {
//  if(Serial.available()>0){
//    char data = Serial.read(); // y o n de python
//    if(data == 'y'){
//      digitalWrite(led,HIGH);
//    }
//    else if(data=='n'){
//      digitalWrite(led,LOW);
//      }
//  }
//}



#include <SoftwareSerial.h>
SoftwareSerial HC06(10, 11); // HC06-TX Pin 10, HC06-RX a Arduino Pin 11

int led = 8; // Usa los pines que desees para el LED

void setup() {
  HC06.begin(9600); // Baudrate 9600, elige tu propia velocidad de baudios
  pinMode(led, OUTPUT); // Establece el pin del LED como salida
}

void loop() {

  if(HC06.available() > 0) // Cuando el HC06 recibe algo
  {
    String receive = HC06.readString(); // Lee desde la comunicación serial como una cadena de texto
    if(receive == "adelante") // Si los datos recibidos son "adelante", enciende el LED
    {
      digitalWrite(led, HIGH);
      delay(500);
    }
    else if(receive == "atras") // Si los datos recibidos son "atras", enciende el LED y hazlo parpadear
    {
      digitalWrite(led, HIGH);
      delay(500);
      digitalWrite(led, HIGH);
      delay(500);
    }
    else
    {
      digitalWrite(led, LOW); // Si se recibe cualquier otro dato, apaga el LED
    }
  }

}
