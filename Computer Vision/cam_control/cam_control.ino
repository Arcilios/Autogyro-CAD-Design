#include <Servo.h>

Servo servoPan;   // FS90R (水平旋转)
Servo servoTilt;  // MG90S (俯仰)

String inputString = ""; 
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
  servoPan.attach(9);   // FS90R
  servoTilt.attach(10); // MG90S
  inputString.reserve(20);
  servoPan.write(92);   // 停止
  servoTilt.write(90);  // 居中
}

void loop() {
  if (stringComplete) {
    parseCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') stringComplete = true;
  }
}

void parseCommand(String cmd) {
  int pIndex = cmd.indexOf('P');
  int tIndex = cmd.indexOf('T');
  int nIndex = cmd.indexOf('\n');

  if (pIndex != -1 && tIndex != -1 && nIndex != -1) {
    int pan = constrain(cmd.substring(pIndex + 1, tIndex).toInt(), 0, 180);
    int tilt = constrain(cmd.substring(tIndex + 1, nIndex).toInt(), 0, 180);

    servoPan.write(pan);
    servoTilt.write(tilt);

    Serial.print("Pan = "); Serial.print(pan);
    Serial.print(", Tilt = "); Serial.println(tilt);
  }
}
