# Vector Clock

A Flask service demonstrating Vector Clocks for tracking causal relationships between events in distributed systems.

## Features

- Logical clock increments
- Clock merge on received events
- Causal ordering comparison
- Concurrent-event detection
- Thread-safe operations
- Clock reset
- Health endpoint
- Pytest test suite

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/clock` | Current vector clock |
| POST | `/api/tick` | Create a local event |
| POST | `/api/receive` | Merge a remote clock |
| POST | `/api/compare` | Compare clocks |
| POST | `/api/reset` | Reset the clock |

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Run tests:

```bash
pytest -q
```

## Example

Create an event:

```bash
curl -X POST http://localhost:5000/api/tick
```

Merge another node:

```bash
curl -X POST http://localhost:5000/api/receive   -H "Content-Type: application/json"   -d '{"clock":{"node-b":4}}'
```

Compare clocks:

```bash
curl -X POST http://localhost:5000/api/compare   -H "Content-Type: application/json"   -d '{"clock":{"node-b":5}}'
```

## Architecture

```text
Node A                         Node B
  |                              |
Event A                       Event B
  |                              |
[A:1,B:0]                    [A:0,B:1]
  |                              |
  +----------- merge ------------+
                 |
                 v
             [A:1,B:1]
```

If neither clock is completely less than the other, the events are concurrent.

## Learning Goals

Logical clocks, causal ordering, distributed event relationships, concurrency detection, and conflict-resolution foundations for distributed databases and replicated systems.
