"""Tests for /api/v1/history.

`test_history_real_db_unavailable_returns_503` uses the real, un-mocked HistoryService to
prove the graceful-degradation behavior verified manually in Step 7: no reachable MongoDB
-> a clean 503, not a crash.
"""


def test_list_history_empty(client):
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}


def test_get_history_record_not_found(client):
    response = client.get("/api/v1/history/not-a-real-id")
    assert response.status_code == 404
    assert response.json()["error"] == "HistoryNotFoundException"


def test_history_real_db_unavailable_returns_503(real_dependencies_client):
    response = real_dependencies_client.get("/api/v1/history")
    assert response.status_code == 503
    assert response.json()["error"] == "DatabaseConnectionException"
