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
    if (accel != 3 ){
      Serial.print("Calibration Status : System : ");
      Serial.print(system, DEC);
      Serial.print(" Gyro : ");
      Serial.print(gyro, DEC);
      Serial.print(" Accel : ");
      Serial.print(accel, DEC);
      Serial.print(" Mag : ");
      Serial.println(mag, DEC);
      delay(500);
    }

    uint8_t x, y, z = 0;
    uint8_t x_offset, y_offset, z_offset = 0;
    uint8_t x_initial, y_initial, z_initial = 0;
    
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    x = euler.x();
    x_initial = 180; //93
    // y = euler.y();
    // y_initial = 76; //76
    z = euler.z();
    z_initial = 162;
    // if (x > 0 && x < 5){
    //   x = 0;
    // }
    if (x < -90){
      x = -90;
    }
    // if (y > 180){
    //   y -= 360;
    // }
    // if (y > 0 && y < 5){
    //   y = 0;
    // }
    // if (z > 0 && z < 5 || z > 240){
    //   z = 0;
    // }
    Serial.print(" X: ");
    Serial.print(x-x_initial);
    // Serial.print(" Y: ");
    // Serial.print(y-y_initial);
    Serial.print(" \tZ: ");
    Serial.print(z-z_initial);
    Serial.println("\t\t");
    delay(500);
}