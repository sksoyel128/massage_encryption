# app.py
from flask import Flask, render_template, request, redirect, url_for, send_file
from node import Network
import os
from datetime import datetime

app = Flask(__name__)

# Configure routing algo and session persistence via environment or defaults
ROUTING_ALGO = os.environ.get("ROUTING_ALGO", "dijkstra").lower()  # "dijkstra" or "aodv"
PERSIST_SESSIONS = os.environ.get("PERSIST_SESSIONS", "false").lower() in ("1", "true", "yes")

network = Network(size=10, routing_algo=ROUTING_ALGO, persist_sessions=PERSIST_SESSIONS)

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "log.txt")
os.makedirs(DATA_DIR, exist_ok=True)

def write_logs(logs):
    # Write logs with UTF-8 encoding so special chars (→ etc.) don't break on Windows
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(logs))

@app.route("/")
def index():
    return render_template(
        "index.html",
        nodes=list(range(network.size)),
        routing_algo=network.routing_algo,
        persist_sessions=network.persist_sessions,
        path=[],
        logs=[],
        decrypted=None,
        src=None,
        dst=None,
        message=None
    )


@app.route("/send", methods=["POST"])
def send():
    try:
        src = int(request.form["source"])
        dst = int(request.form["destination"])
        message = request.form["message"].strip()

        if src == dst:
            path = [src]
            logs = [f"{datetime.now().isoformat()}  Source and destination are same (Node {src})."]
            decrypted = message
            write_logs(logs)
            return render_template("index.html", nodes=list(range(network.size)),
                                   path=path, logs=logs, decrypted=decrypted,
                                   src=src, dst=dst, message=message,
                                   routing_algo=network.routing_algo, persist_sessions=network.persist_sessions)

        path, logs, decrypted = network.send_message(src, dst, message)
        # prepend timestamp to each log line
        time = datetime.now().isoformat()
        logs = [f"{time}  {line}" for line in logs]
        write_logs(logs)

        return render_template("index.html", nodes=list(range(network.size)),
                               path=path, logs=logs, decrypted=decrypted,
                               src=src, dst=dst, message=message,
                               routing_algo=network.routing_algo, persist_sessions=network.persist_sessions)
    except Exception as e:
        # Capture unexpected errors and write to log
        err = f"Error: {type(e).__name__}: {e}"
        write_logs([err])
        return render_template("index.html", nodes=list(range(network.size)), logs=[err]), 500

@app.route("/download-log")
def download_log():
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, as_attachment=True)
    return redirect(url_for("index"))

from flask import jsonify

@app.route("/network/add_edge", methods=["POST"])
def add_edge():
    data = request.json
    try:
        node1 = int(data.get("node1"))
        node2 = int(data.get("node2"))
        cost = int(data.get("cost"))
        network.add_edge(node1, node2, cost)
        return jsonify({"status": "success", "message": f"Edge added between Node {node1} and Node {node2} with cost {cost}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/network/remove_edge", methods=["POST"])
def remove_edge():
    data = request.json
    try:
        node1 = int(data.get("node1"))
        node2 = int(data.get("node2"))
        network.remove_edge(node1, node2)
        return jsonify({"status": "success", "message": f"Edge removed between Node {node1} and Node {node2}"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/network/node_offline", methods=["POST"])
def node_offline():
    data = request.json
    try:
        node = int(data.get("node"))
        network.set_node_offline(node)
        return jsonify({"status": "success", "message": f"Node {node} set offline"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/network/node_online", methods=["POST"])
def node_online():
    data = request.json
    try:
        node = int(data.get("node"))
        connections = data.get("connections", {})
        # connections expected as dict with string keys, convert keys to int
        connections_int = {int(k): int(v) for k, v in connections.items()}
        network.set_node_online(node, connections_int)
        return jsonify({"status": "success", "message": f"Node {node} set online with connections"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    
@app.route("/network-data")
def network_data():
    nodes = [{"id": i} for i in range(network.size)]
    edges = []
    for i in range(network.size):
        for j in range(i + 1, network.size):
            cost = network.adj_matrix[i][j]
            if cost and cost > 0:
                edges.append({"from": i, "to": j, "cost": cost})
    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    # Run in debug for development; remove debug=True for production
    app.run(debug=True)
