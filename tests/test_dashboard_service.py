from app.services.monitor_service import get_dashboard_stats


def test_get_dashboard_stats_returns_correct_statistics(mock_db):

    # Arrange
    mock_db.scalar.side_effect = [
        6,
        5,
        100,
        95,
        350
    ]

    # Act
    result = get_dashboard_stats(mock_db)

    # Assert
    assert result["total_monitors"] == 6
    assert result["active_monitors"] == 5
    assert result["total_checks"] == 100
    assert result["successful_checks"] == 95
    assert result["failed_checks"] == 5
    assert result["overall_uptime_percentage"] == 95.0
    assert result["average_response_time_ms"] == 350

    assert mock_db.scalar.call_count == 5


def test_get_dashboard_stats_returns_zero_uptime_when_no_checks_exist(mock_db):

    # Arrange
    mock_db.scalar.side_effect = [
        6,
        5,
        0,
        0,
        0
    ]

    # Act
    result = get_dashboard_stats(mock_db)

    # Assert
    assert result["total_monitors"] == 6
    assert result["active_monitors"] == 5
    assert result["total_checks"] == 0
    assert result["successful_checks"] == 0
    assert result["failed_checks"] == 0
    assert result["overall_uptime_percentage"] == 0
    assert result["average_response_time_ms"] == 0

    assert mock_db.scalar.call_count == 5