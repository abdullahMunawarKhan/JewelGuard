# Jewellery Shop Security Dashboard (Local Prototype)

Arduino Uno + HC-SR501 PIR + local Python dashboard over USB. No Wi-Fi/Bluetooth module or cloud account required.

The sketch expects the HC-SR501 OUT pin to go HIGH when motion is detected and LOW when the area is clear.

## Wiring

- HC-SR501 VCC -> Arduino 5V
- HC-SR501 OUT -> D2
- HC-SR501 GND -> GND
- Red LED anode -> D7 through 220 ohm resistor; cathode -> GND
- Green LED anode -> D6 through 220 ohm resistor; cathode -> GND
- Active 5V buzzer positive -> D8; negative -> GND

Use a small active buzzer that is safe for an Arduino GPIO. If its current requirement exceeds the GPIO rating, use a transistor driver. Verify the PIR module labels before powering it.

## 1. Upload Arduino code

1. Open `arduino/jewellery_security_alarm.ino` in Arduino IDE.
2. Select **Tools > Board > Arduino Uno** and the correct **Tools > Port**.
3. Upload the sketch.
4. Close Arduino IDE Serial Monitor before starting the dashboard. Only one app can normally use the serial port at a time.

The PIR sensor may need 30–60 seconds or longer to stabilize after power-up.

## 2. Install Python dependencies (Windows)

Open Command Prompt in this project folder:

```bat
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

If `py` is not recognized, install Python 3 from python.org and enable the option to add Python to PATH.

## 3. Start the dashboard

```bat
py app.py
```

Open this address on the same laptop:

http://127.0.0.1:5000

Choose the Arduino COM port from the dropdown and click **Connect**.

## Troubleshooting

- **No serial ports:** reconnect USB, try another data-capable USB cable, check Windows Device Manager, then click Refresh.
- **Access denied / port busy:** close Arduino IDE Serial Monitor and any other app using that COM port.
- **No motion events:** allow PIR warm-up time, check VCC/GND/OUT wiring, and verify that the sketch is uploaded.
- **Buzzer doesn't sound:** confirm it is an active buzzer and check its polarity and current requirements.
- **Dashboard is disconnected after upload:** restarting the Arduino may be normal; reconnect the selected COM port in the dashboard.

## Current limitations

- This is a local prototype; it does not send phone notifications or cloud alerts.
- The Python process and USB connection must remain active for dashboard updates.
- Event history is kept in memory and clears when the app restarts.
- The physical alarm is controlled by the Arduino and does not depend on the dashboard.
- This prototype is not a certified security system and should not be used as the sole protection for a jewellery shop.
