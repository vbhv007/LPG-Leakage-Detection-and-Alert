#include <MQ2.h>
#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ThingSpeak.h>;

const char *ssid = "enter ssid";
const char *pass = "enter password";
unsigned long lpgChannel = 748890;
unsigned long coChannel = 748891;
unsigned long smokeChannel = 748892;
const char *lpgKey = "key for lpg channel";
const char *coKey = "key for co channel";
const char *smokeKey = "key for smoke channel";
const char *server = "api.thingspeak.com";
WiFiClient client;
int Analog_Input = A0;
//#define buzzer D0
int lpg, co, smoke;

MQ2 mq2(Analog_Input);

void setup()
{
  Serial.begin(9600);
  Serial.println("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  ThingSpeak.begin(client);
  mq2.begin();
  //pinMode(buzzer, OUTPUT);
  Serial.println("Setup complete.");
}

void dataPrint(int lpg, int co, int smoke)
{
  Serial.print("LPG: ");
  Serial.print(lpg);
  Serial.print("  ");
  Serial.print("CO: ");
  Serial.print(co);
  Serial.print("  ");
  Serial.print("Smoke: ");
  Serial.println(smoke);
}

void loop()
{
  //digitalWrite(buzzer, LOW);
  float *values = mq2.read(false); //set it false if you don't want to print the values in the Serial
  //lpg = values[0];
  lpg = mq2.readLPG();
  //co = values[1];
  co = mq2.readCO();
  //smoke = values[2];
  smoke = mq2.readSmoke();
  while (lpg >= 60 or co >= 100 or smoke >= 100)
  {
    float *values = mq2.read(false);
    lpg = mq2.readLPG();
    co = mq2.readCO();
    smoke = mq2.readSmoke();
    dataPrint(lpg, co, smoke);
    Serial.println("Threshold reached! Sending data to cloud.");
    ThingSpeak.writeField(lpgChannel, 1, lpg, lpgKey);
    ThingSpeak.writeField(coChannel, 1, co, coKey);
    ThingSpeak.writeField(smokeChannel, 1, smoke, smokeKey);
    Serial.println("Data sent to cloud.");
    Serial.println("Going to sleep for 30 secs");
    delay(30000);
  }
  dataPrint(lpg, co, smoke);
  Serial.println("Normal readings. Sending data to cloud.");
  ThingSpeak.writeField(lpgChannel, 1, lpg, lpgKey);
  ThingSpeak.writeField(coChannel, 1, co, coKey);
  ThingSpeak.writeField(smokeChannel, 1, smoke, smokeKey);
  Serial.println("Data sent to cloud.");
  //digitalWrite(buzzer, HIGH);
  Serial.println("Going to sleep for 30 secs");
  //digitalWrite(buzzer, LOW);
  delay(30000);
}
