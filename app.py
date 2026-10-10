
from collections import deque
from datetime import datetime
import threading
import time

import serial
from serial.tools import list_ports
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BAUD_RATE = 9600
events = deque(maxlen=500)
lock = threading.Lock()

state = {
    "connected": False,
    "port": None,
    "motion": False,
    "alarm": False,
    "last_message": None,
    "last_seen": None,
    "error": None,
}

reader_thread = None
stop_event = threading.Event()


def add_event(event_type, message):
    event = {
        "id": time.time_ns(),
        "time": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "type": event_type,
        "message": message,
    }

    with lock:
        events.appendleft(event)


def serial_reader(port_name):
    try:
        with serial.Serial(
            port_name,
            BAUD_RATE,
            timeout=1
        ) as ser:

            # Arduino Uno may reset when serial opens.
            time.sleep(2)

            with lock:
                state["connected"] = True
                state["port"] = port_name
                state["error"] = None

            add_event(
                "SYSTEM",
                f"Connected to Arduino on {port_name}"
            )

            while not stop_event.is_set():
                raw = ser.readline()

                if not raw:
                    continue

                line = raw.decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                if not line:
                    continue

                with lock:
                    state["last_message"] = line
                    state["last_seen"] = (
                        datetime.now()
                        .astimezone()
                        .isoformat(timespec="seconds")
                    )
                    state["error"] = None

                if line == "EVENT:MOTION_DETECTED":
                    with lock:
                        state["motion"] = True
                        state["alarm"] = True

                    add_event(
                        "ALERT",
                        "Motion detected — local alarm activated"
                    )

                elif line == "EVENT:AREA_CLEAR":
                    with lock:
                        was_motion = state["motion"]
                        state["motion"] = False
                        state["alarm"] = False

                    if was_motion:
                        add_event(
                            "NORMAL",
                            "Area clear — system is armed"
                        )

                elif line == "SYSTEM:READY":
                    add_event(
                        "SYSTEM",
                        "Arduino is ready"
                    )

    except Exception as exc:
        with lock:
            state["connected"] = False
            state["port"] = None
            state["error"] = str(exc)

        add_event(
            "ERROR",
            f"Serial connection ended: {exc}"
        )

    finally:
        with lock:
            state["connected"] = False
            state["port"] = None


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/status")
def api_status():
    with lock:
        snapshot = dict(state)

    return jsonify(snapshot)


@app.get("/api/events")
def api_events():
    with lock:
        snapshot = list(events)

    return jsonify(snapshot)


@app.get("/api/ports")
def api_ports():
    ports = [
        {
            "device": port.device,
            "description": port.description
        }
        for port in list_ports.comports()
    ]

    return jsonify(ports)


@app.post("/api/connect")
def api_connect():
    global reader_thread

    body = request.get_json(silent=True) or {}
    port_name = body.get("port", "").strip()

    if not port_name:
        return jsonify({
            "ok": False,
            "error": "Select a serial port first."
        }), 400

    if reader_thread and reader_thread.is_alive():
        return jsonify({
            "ok": False,
            "error": (
                "A serial reader is already running. "
                "Restart the app if necessary."
            )
        }), 409

    stop_event.clear()

    reader_thread = threading.Thread(
        target=serial_reader,
        args=(port_name,),
        daemon=True
    )

    reader_thread.start()

    return jsonify({
        "ok": True,
        "message": f"Connecting to {port_name}"
    })


@app.post("/api/disconnect")
def api_disconnect():
    stop_event.set()

    return jsonify({
        "ok": True,
        "message": (
            "Disconnect requested. Restart the app "
            "if the serial connection does not close."
        )
    })


if __name__ == "__main__":
    print("\nJewellery Shop Security Dashboard")
    print("Open http://127.0.0.1:5000 in your browser.")
    print("Close Arduino IDE Serial Monitor before connecting.\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
