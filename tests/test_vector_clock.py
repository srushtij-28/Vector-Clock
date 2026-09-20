import pytest
import app as m


@pytest.fixture()
def client():
    m.clock = m.VectorClock("node-a")
    m.app.config["TESTING"] = True
    with m.app.test_client() as c:
        yield c


def test_tick(client):
    data = client.post("/api/tick").get_json()
    assert data["clock"]["node-a"] == 1


def test_receive_merges_and_ticks(client):
    data = client.post("/api/receive", json={"clock": {"node-b": 4}}).get_json()
    assert data["clock"] == {"node-a": 1, "node-b": 4}


def test_before(client):
    data = client.post("/api/compare", json={"clock": {"node-a": 2}}).get_json()
    assert data["relation"] == "before"


def test_after(client):
    client.post("/api/tick")
    data = client.post("/api/compare", json={"clock": {"node-a": 0}}).get_json()
    assert data["relation"] == "after"


def test_concurrent(client):
    client.post("/api/tick")
    data = client.post("/api/compare", json={"clock": {"node-b": 1}}).get_json()
    assert data["relation"] == "concurrent"


def test_equal(client):
    data = client.post("/api/compare", json={"clock": {"node-a": 0}}).get_json()
    assert data["relation"] == "equal"


def test_invalid_clock(client):
    response = client.post("/api/receive", json={"clock": {"node-b": -1}})
    assert response.status_code == 400


def test_reset(client):
    data = client.post("/api/reset", json={"node_id": "node-x"}).get_json()
    assert data["clock"] == {"node-x": 0}
