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
    

    uint8_t x, y, z = 0;
    
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    Serial.print(" X: ");
    Serial.println(-(euler.x()-76-35+90));
    Serial.print("Y: ");
    Serial.println(-(euler.y()-40-20));
    Serial.print("Z: ");
    Serial.print(-(euler.z()));
    Serial.println("\t\t");
    delay(1000);
}