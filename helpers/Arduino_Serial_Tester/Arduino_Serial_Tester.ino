// [ARDUINO SERIAL TESTER]
// David Miguel Garcia Palacios
// Universidad Nacional de Colombia Sede Bogota

// Parametros
int baudios = 9600;
String comando = "";

// Inicializacion del serial
void setup() {
  Serial.begin(baudios);
}

// Respuesta a comandos seriales
void loop() {
  if (Serial.available() > 0){
    comando = Serial.readStringUntil("\n");
    comando.trim();
    if(comando == "marco"){
      Serial.println("polo");
    }
  } else {
    Serial.println("ping");
  }
  delay(1000);

}
