"""Morocco 30-Day Content Calendar — Flask App"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "calendar_data.json")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)


def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", data=data)


@app.route("/api/calendar")
def api_calendar():
    return jsonify(load_data())


@app.route("/api/day/<date_str>", methods=["PUT"])
def api_update_day(date_str):
    data = load_data()
    for i, day in enumerate(data["days"]):
        if day["date"] == date_str:
            updates = request.get_json()
            data["days"][i].update(updates)
            save_data(data)
            return jsonify({"status": "ok", "day": data["days"][i]})
    return jsonify({"error": "Date not found"}), 404


@app.route("/api/day", methods=["POST"])
def api_add_day():
    data = load_data()
    new_day = request.get_json()
    data["days"].append(new_day)
    data["days"].sort(key=lambda d: d["date"])
    save_data(data)
    return jsonify({"status": "ok", "day": new_day}), 201


import socket

def get_local_ip():
    try:
        # Create a dummy socket to determine the local routing IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 5055
    print("\n" + "=" * 50)
    print("  🇲🇦 Morocco Content Calendar")
    print(f"  Desktop URL: http://localhost:{port}")
    print(f"  Mobile URL:  http://{local_ip}:{port}")
    print("  (Ensure your iPhone is on the same Wi-Fi network)")
    print("=" * 50 + "\n")
    app.run(host="0.0.0.0", port=port, debug=True)
