#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#define BNO055_SAMPLERATE_DELAY_MS (100)
  
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

void setup() {
  Serial.begin(115200);
  if(!bno.begin()) {
    Serial.println("Could not find a valid BNO055 sensor, check wiring!");
    while(1);
  }
  delay(1000);
  bno.setExtCrystalUse(true); // Use external crystal for more accurate readings
}

void loop() {
    uint8_t system, gyro, accel, mag = 0;
    bno.getCalibration(&system, &gyro, &accel, &mag); 
    Serial.print("Calibration Status : System : ");
    Serial.print(system, DEC);
    Serial.print(" Gyro : ");
    Serial.print(gyro, DEC);
    Serial.print(" Accel : ");
    Serial.print(accel, DEC);
    Serial.print(" Mag : ");
    Serial.println(mag, DEC);
    delay(1000);
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    Serial.print(" Joint Angle: ");
    Serial.print(-(euler.z()-105));
    Serial.print("\t\t");
    delay(1000);

}

