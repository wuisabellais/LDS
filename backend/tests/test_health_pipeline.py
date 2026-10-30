def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_pipeline(client):
    response = client.get("/api/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "測試管線"
    assert data["content_type"] == "原油"
    assert data["length_m"] == 25000.0
