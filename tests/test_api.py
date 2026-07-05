def test_create_monitor(client, sample_monitor_payload):

    response = client.post(
        "/monitors/",
        json=sample_monitor_payload
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == sample_monitor_payload["name"]
    assert data["url"] == "https://google.com/"
    assert data["status"] == "ACTIVE"
    assert data["interval_minutes"] == sample_monitor_payload["interval_minutes"]

    assert "id" in data
    assert "created_at" in data

def test_get_all_monitors(client, sample_monitor_payload):

    client.post(
        "/monitors/",
        json=sample_monitor_payload
    )

    response = client.get("/monitors/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1

    assert data[0]["name"] == sample_monitor_payload["name"]
    assert data[0]["url"] == "https://google.com/"
    assert data[0]["interval_minutes"] == 5

def test_get_monitor_by_id(client, sample_monitor_payload):

    # Arrange
    create_response = client.post(
        "/monitors/",
        json=sample_monitor_payload
    )

    monitor_id = create_response.json()["id"]

    # Act
    response = client.get(f"/monitors/{monitor_id}")

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == monitor_id
    assert data["name"] == sample_monitor_payload["name"]
    assert data["url"] == "https://google.com/"

def test_get_monitor_returns_404_for_invalid_id(client):

    response = client.get("/monitors/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitor not found"

def test_update_monitor(client, sample_monitor_payload):

    # Arrange
    create_response = client.post(
        "/monitors/",
        json=sample_monitor_payload
    )

    monitor_id = create_response.json()["id"]

    updated_payload = {
        "name": "GitHub",
        "url": "https://github.com",
        "interval_minutes": 10
    }

    # Act
    response = client.put(
        f"/monitors/{monitor_id}",
        json=updated_payload
    )

    # Assert
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == monitor_id
    assert data["name"] == "GitHub"
    assert data["url"] == "https://github.com/"
    assert data["interval_minutes"] == 10

def test_update_monitor_returns_404_for_invalid_id(client):

    updated_payload = {
        "name": "GitHub",
        "url": "https://github.com",
        "interval_minutes": 10
    }

    response = client.put(
        "/monitors/99999",
        json=updated_payload
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitor not found"

def test_delete_monitor(client, sample_monitor_payload):

    # Arrange
    create_response = client.post(
        "/monitors/",
        json=sample_monitor_payload
    )

    monitor_id = create_response.json()["id"]

    # Act
    response = client.delete(f"/monitors/{monitor_id}")

    # Assert
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/monitors/{monitor_id}")

    assert response.status_code == 404

def test_delete_monitor_returns_404_for_invalid_id(client):

    response = client.delete("/monitors/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Monitor not found"

from app.models.monitor import Monitor
from app.models.monitor_check import MonitorCheck


def test_dashboard_endpoint(client, db):

    monitor = Monitor(
        name="Google",
        url="https://google.com",
        interval_minutes=5
    )

    db.add(monitor)
    db.commit()
    db.refresh(monitor)

    db.add_all([
        MonitorCheck(
            monitor_id=monitor.id,
            status_code=200,
            response_time_ms=250,
            is_up=True
        ),
        MonitorCheck(
            monitor_id=monitor.id,
            status_code=500,
            response_time_ms=500,
            is_up=False
        )
    ])

    db.commit()

    response = client.get("/monitors/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert data["total_monitors"] == 1
    assert data["active_monitors"] == 1
    assert data["total_checks"] == 2
    assert data["successful_checks"] == 1
    assert data["failed_checks"] == 1
    assert data["overall_uptime_percentage"] == 50.0
    assert data["average_response_time_ms"] == 375

def test_monitor_stats_endpoint(client, db):

    monitor = Monitor(
        name="Google",
        url="https://google.com",
        interval_minutes=5
    )

    db.add(monitor)
    db.commit()
    db.refresh(monitor)

    db.add_all([
        MonitorCheck(
            monitor_id=monitor.id,
            status_code=200,
            response_time_ms=300,
            is_up=True
        ),
        MonitorCheck(
            monitor_id=monitor.id,
            status_code=200,
            response_time_ms=500,
            is_up=True
        ),
        MonitorCheck(
            monitor_id=monitor.id,
            status_code=500,
            response_time_ms=700,
            is_up=False
        )
    ])

    db.commit()

    response = client.get(
        f"/monitors/{monitor.id}/stats"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["monitor_id"] == monitor.id
    assert data["total_checks"] == 3
    assert data["successful_checks"] == 2
    assert data["failed_checks"] == 1
    assert data["uptime_percentage"] == 66.67
    assert data["average_response_time_ms"] == 500

def test_monitor_health_endpoint(client, db):

    monitor = Monitor(
        name="Google",
        url="https://google.com",
        interval_minutes=5
    )

    db.add(monitor)
    db.commit()
    db.refresh(monitor)

    check = MonitorCheck(
        monitor_id=monitor.id,
        status_code=200,
        response_time_ms=250,
        is_up=True
    )

    db.add(check)

    db.commit()

    response = client.get(
        f"/monitors/{monitor.id}/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["monitor_id"] == monitor.id
    assert data["status"] == "UP"
    assert data["last_status_code"] == 200
    assert data["last_response_time_ms"] == 250