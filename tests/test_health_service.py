import pytest
from fastapi import HTTPException

from app.models.monitor import Monitor
from app.services.monitor_service import get_monitor_health


def test_get_monitor_health_returns_up_when_latest_check_is_up(
    mock_db,
    sample_monitor,
    sample_monitor_up
):

    mock_db.get.return_value = sample_monitor

    mock_db.execute.return_value.scalars.return_value.first.return_value = (
        sample_monitor_up
    )

    result = get_monitor_health(
        monitor_id=1,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status"] == "UP"
    assert result["last_status_code"] == 200
    assert result["last_response_time_ms"] == 250

    mock_db.get.assert_called_once_with(Monitor, 1)
    mock_db.execute.assert_called_once()


def test_get_monitor_health_returns_down_when_latest_check_is_down(
    mock_db,
    sample_monitor,
    sample_monitor_down
):

    mock_db.get.return_value = sample_monitor

    mock_db.execute.return_value.scalars.return_value.first.return_value = (
        sample_monitor_down
    )

    result = get_monitor_health(
        monitor_id=1,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status"] == "DOWN"
    assert result["last_status_code"] == 500
    assert result["last_response_time_ms"] == 5000

    mock_db.get.assert_called_once_with(Monitor, 1)
    mock_db.execute.assert_called_once()


def test_get_monitor_health_raises_404_when_monitor_not_found(mock_db):

    mock_db.get.return_value = None

    with pytest.raises(HTTPException) as exc:

        get_monitor_health(
            monitor_id=1,
            db=mock_db
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


def test_get_monitor_health_raises_404_when_no_checks_found(
    mock_db,
    sample_monitor
):

    mock_db.get.return_value = sample_monitor

    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:

        get_monitor_health(
            monitor_id=1,
            db=mock_db
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "No checks found for monitor"