//#include <ESP8266WiFiType.h>
//#include <WiFiClientSecureAxTLS.h>
//#include <WiFiUdp.h>
//#include <ESP8266WiFiGeneric.h>
//#include <WiFiServerSecureBearSSL.h>
#include <ESP8266WiFi.h>
//#include <CertStoreBearSSL.h>
//#include <WiFiClient.h>
//#include <WiFiServerSecure.h>
//#include <WiFiClientSecure.h>
//#include <ESP8266WiFiSTA.h>
//#include <WiFiServerSecureAxTLS.h>
//#include <WiFiClientSecureBearSSL.h>
//#include <WiFiServer.h>
//#include <ESP8266WiFiScan.h>
//#include <ESP8266WiFiMulti.h>
//#include <ESP8266WiFiAP.h>
#include <ESP8266HTTPClient.h>
//#include <ArduinoJson.h>

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         5          // Configurable, see typical pin layout above
#define SS_PIN          4         // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

const char* ssid = "ruyteador";
const char* password = "ruyteador";

const String lockid = "1";
//const String rfid = "14";

const String unlock_url = "smartlock/unlock";
//const String server_address = "http://192.168.43.221:8000/";
//const String server_address = "http://192.168.0.110:8000/";
const String server_address = "http://192.168.43.45:8000/";

const int LOCK = 0;
const int LED = 2;
const int ERROR_LED = 15;
const int BUTTON = 16;

void setup () {
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(LED, OUTPUT);
  pinMode(ERROR_LED, OUTPUT);
  pinMode(LOCK, OUTPUT);

  Serial.begin(115200);

while (!Serial) {
      delay(1000);
// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
}
  SPI.begin();      // Init SPI bus
  mfrc522.PCD_Init();   // Init MFRC522
  delay(4);       // Optional delay. Some board do need more time after init to be ready, see Readme
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("Connecting..");
  }

}

void loop() {
  Serial.print("Loop starting..");

  digitalWrite(BUTTON, LOW);
  digitalWrite(ERROR_LED, LOW);
  digitalWrite(LED, LOW);
  digitalWrite(LOCK, HIGH);

  if ( ! mfrc522.PICC_IsNewCardPresent()) {
        delay(1000);

    return;
  }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
        delay(1000);

    return;
  }

//  Serial.print(F("Card UID:"));
  String rfid= "";
  Serial.println();
  
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) {
//     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
//     Serial.print(mfrc522.uid.uidByte[i], HEX);
//     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     rfid.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  rfid = rfid.substring(0);

  Serial.println("RFID: " + rfid);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(server_address + unlock_url);
    Serial.print("Connected..");

//    while (digitalRead(BUTTON) != HIGH) {
//      delay(1);
//    }

    const char* headerNames[] = { "Set-Cookie" };
    http.collectHeaders(headerNames, sizeof(headerNames)/sizeof(headerNames[0]));

    int httpCode = http.GET();
 
    if (httpCode > 0) {
       String headers = "";
       
       if (http.hasHeader("Set-Cookie")) {
          headers = http.header("Set-Cookie");
       }
  
      String response = http.getString();

      int value_index1 = headers.indexOf("csrftoken=");
      String value_string1 = headers.substring(value_index1);
      String csrf_token1 = value_string1.substring(10, value_string1.indexOf(";"));
      
      int value_index2 = response.indexOf("value=\"");
      String value_string2 = response.substring(value_index2);
      String csrf_token2 = value_string2.substring(7, value_string2.indexOf("\">"));
     
      http.end();
      http.begin(server_address + unlock_url);
      
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      http.addHeader("Cookie", "csrftoken=" + csrf_token1);

      String postData = "csrfmiddlewaretoken="+ csrf_token2 + "&lockid=" + lockid + "&rfid=" + rfid;

      httpCode = http.POST(postData);
 
      String payload = http.getString();       
      Serial.println(payload);
      if (payload == "request accepted, open") {
          digitalWrite(LED, HIGH);
          digitalWrite(LOCK, LOW);
          delay(1000);
      } else if (payload == "request denied") {
          digitalWrite(ERROR_LED, HIGH);
          delay(1000);
      }
    }
    http.end();
  }

}
