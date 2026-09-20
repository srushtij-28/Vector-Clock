from threading import RLock
from flask import Flask, jsonify, request

app = Flask(__name__)


class VectorClock:
    def __init__(self, node_id):
        if not isinstance(node_id, str) or not node_id:
            raise ValueError("node_id must be a non-empty string")
        self.node_id = node_id
        self.clock = {node_id: 0}
        self.lock = RLock()

    def tick(self):
        with self.lock:
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
            return dict(self.clock)

    def receive(self, incoming):
        if not isinstance(incoming, dict):
            raise ValueError("clock must be an object")
        with self.lock:
            for node, value in incoming.items():
                if not isinstance(node, str) or not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError("clock values must be non-negative integers")
                self.clock[node] = max(self.clock.get(node, 0), value)
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
            return dict(self.clock)

    def compare(self, other):
        if not isinstance(other, dict):
            raise ValueError("clock must be an object")
        with self.lock:
            nodes = set(self.clock) | set(other)
            less = any(self.clock.get(n, 0) < other.get(n, 0) for n in nodes)
            greater = any(self.clock.get(n, 0) > other.get(n, 0) for n in nodes)
            if less and not greater:
                return "before"
            if greater and not less:
                return "after"
            if not less and not greater:
                return "equal"
            return "concurrent"

    def snapshot(self):
        with self.lock:
            return dict(self.clock)


clock = VectorClock("node-1")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "vector-clock"})


@app.get("/api/clock")
def get_clock():
    return jsonify(clock.snapshot())


@app.post("/api/tick")
def tick():
    return jsonify({"clock": clock.tick()})


@app.post("/api/receive")
def receive():
    body = request.get_json(silent=True)
    incoming = body.get("clock") if isinstance(body, dict) else None
    if not isinstance(incoming, dict):
        return jsonify({"error": "JSON body with object 'clock' is required"}), 400
    try:
        result = clock.receive(incoming)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"clock": result})


@app.post("/api/compare")
def compare():
    body = request.get_json(silent=True)
    other = body.get("clock") if isinstance(body, dict) else None
    if not isinstance(other, dict):
        return jsonify({"error": "JSON body with object 'clock' is required"}), 400
    try:
        relation = clock.compare(other)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"relation": relation, "clock": clock.snapshot(), "other": other})


@app.post("/api/reset")
def reset():
    global clock
    body = request.get_json(silent=True) or {}
    try:
        clock = VectorClock(body.get("node_id", "node-1"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"clock": clock.snapshot()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
