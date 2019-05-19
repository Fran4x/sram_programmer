#include "Arduino.h"

#define SHIFT_DATA 2
#define SHIFT_CLOCK 3
#define SHIFT_LATCH 4
#define DATA_PIN 5 // first data pin, 7 others will follow afterwards
#define WRITE_ENABLE 13
#define CHIP_ENABLE A0
#define OUTPUT_ENABLE A1

void high_pulse(int pin) {
  digitalWrite(pin, LOW);
  digitalWrite(pin, HIGH);
  digitalWrite(pin, LOW);
}

void low_pulse(int pin) {
  digitalWrite(pin, HIGH);
  digitalWrite(pin, LOW);
  digitalWrite(pin, HIGH);
}

void set_address(int address) {
  shiftOut(SHIFT_DATA, SHIFT_CLOCK, MSBFIRST, address >> 8);
  shiftOut(SHIFT_DATA, SHIFT_CLOCK, MSBFIRST, address);

  high_pulse(SHIFT_LATCH);
}

void data_read_mode() {
  for (int i = DATA_PIN; i <= DATA_PIN + 7; i++) {
    pinMode(i, INPUT);
  }
}

void data_write_mode() {
  for (int i = DATA_PIN; i <= DATA_PIN + 7; i++) {
    pinMode(i, OUTPUT);
  }
}

int read_byte() {
  int number = 0;
  int temp;
  for (int i = 0; i < 8; i++) {
    temp = (int)digitalRead(DATA_PIN + i);
    temp = temp << i;
    number = number | temp;
  }
  return number;
}

int read(int address) {
  data_read_mode();
  set_address(address);
  digitalWrite(WRITE_ENABLE, HIGH);
  digitalWrite(CHIP_ENABLE, LOW);
  digitalWrite(OUTPUT_ENABLE, LOW);

  int read = read_byte();
  digitalWrite(CHIP_ENABLE, HIGH);
  return read;
}

void write_byte(int address, int byte) {
  set_address(address);

  int temp;
  for (int i = 0; i < 8; i++) {
    temp = byte >> i;
    temp = temp & 1;
    digitalWrite(DATA_PIN + i, (bool)temp);
  }

  digitalWrite(CHIP_ENABLE, LOW);
  digitalWrite(WRITE_ENABLE, LOW);


  digitalWrite(WRITE_ENABLE, HIGH);
  digitalWrite(CHIP_ENABLE, HIGH);

}

void write_prepare() {
  data_write_mode();
  digitalWrite(OUTPUT_ENABLE, HIGH);
  digitalWrite(CHIP_ENABLE, HIGH);
  digitalWrite(WRITE_ENABLE, HIGH);
}

void write(int address, int byte) {
  write_prepare();

  write_byte(address, byte);

  while(read(address)!=byte){
    write_prepare();
    write_byte(address,byte);
  }
}

/*void disable_software_protection() {
  write_prepare();

  write_byte(0x5555, 0xAA);
  write_byte(0x2AAA, 0x55);
  write_byte(0x5555, 0x80);
  write_byte(0x5555, 0xAA);
  write_byte(0x2AAA, 0x55);
  write_byte(0x5555, 0x20);

  delay(15); // wait for write cycle time (tWC)
  digitalWrite(CHIP_ENABLE, LOW);
  }*/

void setup() {

  digitalWrite(CHIP_ENABLE, HIGH);
  digitalWrite(WRITE_ENABLE,
               HIGH); // need to set these pins to high beforehand, otherwise
                      // they will be pulsed low when the arduino is powered on
  pinMode(SHIFT_DATA, OUTPUT);
  pinMode(SHIFT_CLOCK, OUTPUT);
  pinMode(SHIFT_LATCH, OUTPUT);
  pinMode(WRITE_ENABLE, OUTPUT);
  pinMode(CHIP_ENABLE, OUTPUT);
  pinMode(OUTPUT_ENABLE, OUTPUT);

  digitalWrite(CHIP_ENABLE, HIGH);

  Serial.begin(115200);
  Serial.setTimeout(5000);
  Serial.write(0xFF); //Arduino is ready
}

void loop() {
  while (Serial.available() > 0) {
    String instruction = Serial.readStringUntil('\n');
    if (instruction == "r") {
      Serial.println(read(Serial.parseInt()));
    } else if (instruction == "w"){
      int address = Serial.parseInt();
      int data = Serial.parseInt();
      write(address, data);
      Serial.println(); //Write is complete
    }
  }
  
}
