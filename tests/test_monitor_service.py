from app.services.monitor_service import run_monitor_check
import httpx


def test_run_monitor_check_returns_up_for_200_response(
    mocker,
    mock_db,
    sample_monitor
):

    fake_response = mocker.MagicMock()
    fake_response.status_code = 200

    mocker.patch(
        "app.services.monitor_service.httpx.get",
        return_value=fake_response
    )

    result = run_monitor_check(
        monitor=sample_monitor,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status_code"] == 200
    assert result["is_up"] is True

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_run_monitor_check_returns_down_for_404_response(mocker,
    mock_db,
    sample_monitor
):
    
    fake_response = mocker.MagicMock()
    fake_response.status_code = 404

    mocker.patch(
        "app.services.monitor_service.httpx.get",
        return_value=fake_response
    )

    result = run_monitor_check(
        monitor=sample_monitor,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status_code"] == 404
    assert result["is_up"] is False

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_run_monitor_check_returns_down_for_500_response(mocker,
    mock_db,
    sample_monitor
):
    
    fake_response = mocker.MagicMock()
    fake_response.status_code = 500

    mocker.patch(
        "app.services.monitor_service.httpx.get",
        return_value=fake_response
    )

    result = run_monitor_check(
        monitor=sample_monitor,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status_code"] == 500
    assert result["is_up"] is False

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_run_monitor_check_returns_up_for_301_response(mocker,
    mock_db,
    sample_monitor
):
    

    fake_response = mocker.MagicMock()
    fake_response.status_code = 301

    mocker.patch(
        "app.services.monitor_service.httpx.get",
        return_value=fake_response
    )

    result = run_monitor_check(
        monitor=sample_monitor,
        db=mock_db
    )

    assert result["monitor_id"] == 1
    assert result["status_code"] == 301
    assert result["is_up"] is True

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_run_monitor_check_returns_down_on_request_error(mocker,
    mock_db,
    sample_monitor
):
    
    mocker.patch(
    "app.services.monitor_service.httpx.get",
    side_effect=httpx.RequestError("Connection failed")
    )

    result = run_monitor_check(
        monitor=sample_monitor,
        db=mock_db
    )

    assert result["status_code"] == 0
    assert result["is_up"] is False

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()