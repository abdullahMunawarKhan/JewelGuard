#define PIR_SENSOR 2
#define BUZZER 8

// The HC-SR501 output goes HIGH when motion is detected.
#define MOTION_DETECTED HIGH

bool previousDetection = false;

void setup() {
  pinMode(PIR_SENSOR, INPUT);
  pinMode(BUZZER, OUTPUT);

  digitalWrite(BUZZER, LOW);

  Serial.begin(9600);

  // Notify the existing Flask dashboard
  Serial.println("SYSTEM:READY");

  delay(300);

  bool detected = (digitalRead(PIR_SENSOR) == MOTION_DETECTED);
  previousDetection = detected;

  if (detected) {
    digitalWrite(BUZZER, HIGH);
    Serial.println("EVENT:MOTION_DETECTED");
  } else {
    Serial.println("EVENT:AREA_CLEAR");
  }
}

void loop() {
  bool currentDetection =
      (digitalRead(PIR_SENSOR) == MOTION_DETECTED);

  // Trigger only when the detection state changes
  if (currentDetection != previousDetection) {

    if (currentDetection) {
      // Motion detected
      digitalWrite(BUZZER, HIGH);
      Serial.println("EVENT:MOTION_DETECTED");
    } else {
      // Motion stopped
      digitalWrite(BUZZER, LOW);
      Serial.println("EVENT:AREA_CLEAR");
    }

    previousDetection = currentDetection;
  }

  delay(50);
}
