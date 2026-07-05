import pytest
from fastapi import HTTPException

from app.models.monitor import Monitor
from app.services.monitor_service import get_monitor_stats


def test_get_monitor_stats_returns_correct_statistics(
    mock_db,
    sample_monitor
):

    mock_db.get.return_value = sample_monitor

    mock_db.scalar.side_effect = [
        100,   
        95,    
        350    
    ]

    result = get_monitor_stats(
        monitor_id=1,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["total_checks"] == 100
    assert result["successful_checks"] == 95
    assert result["failed_checks"] == 5
    assert result["uptime_percentage"] == 95.0
    assert result["average_response_time_ms"] == 350

    mock_db.get.assert_called_once_with(Monitor, 1)
    assert mock_db.scalar.call_count == 3


def test_get_monitor_stats_raises_404_when_monitor_not_found(
    mock_db
):

    mock_db.get.return_value = None

    with pytest.raises(HTTPException) as exc:

        get_monitor_stats(
            monitor_id=1,
            db=mock_db
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Monitor not found"


def test_get_monitor_stats_returns_zero_uptime_when_no_checks_exist(
    mock_db,
    sample_monitor
):

    mock_db.get.return_value = sample_monitor

    mock_db.scalar.side_effect = [
        0,      
        0,      
        0       
    ]

    result = get_monitor_stats(
        monitor_id=1,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["total_checks"] == 0
    assert result["successful_checks"] == 0
    assert result["failed_checks"] == 0
    assert result["uptime_percentage"] == 0
    assert result["average_response_time_ms"] == 0

    mock_db.get.assert_called_once_with(Monitor, 1)
    assert mock_db.scalar.call_count == 3


def test_get_monitor_stats_returns_zero_average_response_time_when_none(
    mock_db,
    sample_monitor
):

    mock_db.get.return_value = sample_monitor

    mock_db.scalar.side_effect = [
        100,
        95,
        None
    ]

    result = get_monitor_stats(
        monitor_id=1,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["average_response_time_ms"] == 0

    mock_db.get.assert_called_once_with(Monitor, 1)
    assert mock_db.scalar.call_count == 3