from fastapi.testclient import TestClient
from ServiceB.main import app
import time

client = TestClient(app)

valid_id = "ABC123"
valid_params = {
    "username": "admin",
    "password": "admin",
    "timeoutInSeconds": 10,
    "parameters": {
        "vlan": 534,
        "interfaces": [1, 2, 3, 4]
    }
}


def test_configure_device_success():
    """Тест успешного выполнения"""
    response = client.post(f"/cpe/{valid_id}", json=valid_params)
    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "success"}


def test_configure_device_invalid_id():
    """Тест: Неверный ID (короткий)"""
    response = client.post("/cpe/123", json=valid_params)
    assert response.status_code == 404
    assert response.json()["detail"] == "The requested equipment is not found"


def test_configure_device_wrong_credentials():
    """Тест: Неверные учетные данные"""
    params = valid_params.copy()
    params["username"] = "wrong_user"
    response = client.post(f"/cpe/{valid_id}", json=params)
    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong username or password"



def test_configure_device_timeout_exceeded():
    """Тест: Таймаут больше 60 секунд"""
    params = valid_params.copy()
    params["timeoutInSeconds"] = 61
    response = client.post(f"/cpe/{valid_id}", json=params)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal provisioning exception"


def test_configure_device_execution_time():
    """Тест: Вызов занимает ожидаемое время"""
    params = valid_params.copy()
    params["timeoutInSeconds"] = 3
    start_time = time.time()
    response = client.post(f"/cpe/{valid_id}", json=params)
    end_time = time.time()

    assert response.status_code == 200
    assert response.json() == {"code": 200, "message": "success"}
    assert end_time - start_time >= 3
