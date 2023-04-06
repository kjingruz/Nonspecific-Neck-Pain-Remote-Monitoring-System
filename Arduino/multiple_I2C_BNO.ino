#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

#define BNO055_SAMPLERATE_DELAY_MS (100)

#define SDA_1 21
#define SCL_1 22
#define SDA_2 19
#define SCL_2 23

TwoWire I2Cone = TwoWire(0);
TwoWire I2Ctwo = TwoWire(1);

Adafruit_BNO055 bno1 = Adafruit_BNO055(55, 0x28, &I2Cone);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28, &I2Ctwo);

void setup() {
  I2Cone.begin(SDA_1, SCL_1, 100000);
  I2Ctwo.begin(SDA_2, SCL_2, 100000);
  Serial.begin(115200);
  Serial.println("\nI2C Scanner");
  SerialBT.begin("ESP32_SPP"); // Name of the Bluetooth device
  Serial.println("Bluetooth device is ready to pair");

  bool status1 = bno1.begin();
  if (!status1) {
    Serial.println("Could not find a valid Bno_1 sensor, check wiring!");
    while (1);
  }
  bool status2 = bno2.begin();
  if (!status2) {
    Serial.println("Could not find a valid Bno_2 sensor, check wiring!");
    while (1);
  }
}

void loop() {
  sensors_event_t Head_Sensor;
  sensors_event_t Back_Sensor;
  bno1.getEvent(&Head_Sensor);
  float head_lean = Head_Sensor.orientation.y;
  float head_shift = Head_Sensor.orientation.z;
  bno2.getEvent(&Back_Sensor);
  float back_lean = Back_Sensor.orientation.y;
  float back_shift = Back_Sensor.orientation.z+90;

  String data = String(back_shift, 4) + "," + String(back_lean, 4) + "," + String(head_lean, 4) + "," + String(head_shift, 4);
  Serial.println(data);
  SerialBT.println(data);

  delay(2000);
}
