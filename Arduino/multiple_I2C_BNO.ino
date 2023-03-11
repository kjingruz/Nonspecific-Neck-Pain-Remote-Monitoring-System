//Import Libraries
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <SoftwareSerial.h>

#define BNO055_SAMPLERATE_DELAY_MS (100)

#define SDA_1 21
#define SCL_1 22
//here we define the pins for the other I2C line that you wired in part 1 of the tutorial
#define SDA_2 19
#define SCL_2 23

TwoWire I2Cone = TwoWire(0);
TwoWire I2Ctwo = TwoWire(1);

Adafruit_BNO055 bno1 = Adafruit_BNO055(55, 0x28, &I2Cone);
Adafruit_BNO055 bno2 = Adafruit_BNO055(55, 0x28, &I2Ctwo);

SoftwareSerial SerialPython(10, 11);  // RX, TX
 
void setup() {
  I2Cone.begin(SDA_1, SCL_1, 100000);
  I2Ctwo.begin(SDA_2, SCL_2, 100000);
  Serial.begin(115200);
  SerialPython.begin(9600);  // Open serial communication with Python
  Serial.println("\nI2C Scanner");

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
  // Calibrate both sensors
  // Serial.println("Calibrating sensors, please wait...");
  // while (!bno1.isFullyCalibrated() || !bno2.isFullyCalibrated()) {
  //   delay(1000);
  // }
  // Serial.println("Calibration done!");

}

void loop() {
  /* Get a new sensor event */
  sensors_event_t Back_Sensor;
  sensors_event_t Head_Sensor;
  bno1.getEvent(&Back_Sensor);
  /* Display the floating point data */
  Serial.print("\tBack Shift (left - and right +): ");
  float back_shift = -Back_Sensor.orientation.y;
  Serial.print(back_shift, 4);
  Serial.print("\tBack Lean (forward + and Back -): ");
  float back_lean = Back_Sensor.orientation.z+90;
  Serial.print(back_lean, 4);
  Serial.println("");
  bno2.getEvent(&Head_Sensor);
  Serial.print("\tHead Lean (forward + and Back -): ");
  float head_lean = -Head_Sensor.orientation.y;
  Serial.print(head_lean, 4);
  Serial.print("\tHead Shift (left - and right +): ");
  float head_shift = -Head_Sensor.orientation.z;
  Serial.print(head_shift, 4);
  Serial.println("");

  String data = String(back_shift, 4) + "," + String(back_lean, 4) + "," + String(head_lean, 4) + "," + String(head_shift, 4);
  SerialPython.println(data);

  delay(1000);
}
 

