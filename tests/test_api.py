import pytest
import requests
import json

BASE_URL = "http://localhost:8000"

API_TEST_DATA = {
    "beauty_title": "пер. ",
    "title": "API Тестовый",
    "other_titles": "API Тест",
    "connect": "",
    "add_time": "2023-02-01 10:00:00",
    "user": {
        "email": "api_test@example.com",
        "fam": "APIТестов",
        "name": "APIТест",
        "otc": "APIТестович",
        "phone": "+78880009988"
    },
    "coords": {
        "latitude": "46.0000",
        "longitude": "8.0000",
        "height": "1100"
    },
    "level": {
        "winter": "",
        "summer": "1Б",
        "autumn": "",
        "spring": ""
    },
    "images": []
}


@pytest.fixture
def created_pereval_id():
    """Фикстура создает перевал через API и возвращает его ID"""
    response = requests.post(f"{BASE_URL}/submitData", json=API_TEST_DATA)
    assert response.status_code == 200
    result = response.json()
    pereval_id = result['id']
    yield pereval_id


def test_post_submitdata():
    """Тест метода POST /submitData"""
    response = requests.post(f"{BASE_URL}/submitData", json=API_TEST_DATA)

    assert response.status_code == 200
    result = response.json()
    assert result['status'] == 200
    assert result['message'] is None
    assert isinstance(result['id'], int)

    print(f"POST /submitData: создан перевал ID {result['id']}")


def test_get_submitdata_by_id(created_pereval_id):
    """Тест метода GET /submitData/{id}"""
    response = requests.get(f"{BASE_URL}/submitData/{created_pereval_id}")

    assert response.status_code == 200
    pereval = response.json()
    assert pereval['id'] == created_pereval_id
    assert 'raw_data' in pereval

    print(f"GET /submitData/{created_pereval_id}: получены данные")


def test_patch_submitdata(created_pereval_id):
    """Тест метода PATCH /submitData/{id}"""
    update_data = API_TEST_DATA.copy()
    update_data['title'] = 'API Обновленное'
    update_data['coords']['latitude'] = '47.0000'

    response = requests.patch(
        f"{BASE_URL}/submitData/{created_pereval_id}",
        json=update_data
    )

    assert response.status_code == 200
    result = response.json()
    assert result['state'] == 1
    assert result['message'] is None

    print(f"PATCH /submitData/{created_pereval_id}: успешно обновлен")


def test_get_submitdata_by_email():
    """Тест метода GET /submitData/?user__email=..."""
    email = API_TEST_DATA['user']['email']
    response = requests.get(
        f"{BASE_URL}/submitData/",
        params={"user__email": email}
    )

    assert response.status_code == 200
    result = response.json()
    assert 'count' in result
    assert 'results' in result
    assert isinstance(result['results'], list)

    print(f"GET /submitData/?user__email={email}: найдено {result['count']} записей")


def test_integration_flow():
    """Интеграционный тест: полный цикл работы API"""
    response = requests.post(f"{BASE_URL}/submitData", json=API_TEST_DATA)
    assert response.status_code == 200
    pereval_id = response.json()['id']
    print(f"1. Добавлен перевал ID: {pereval_id}")

    response = requests.get(f"{BASE_URL}/submitData/{pereval_id}")
    assert response.status_code == 200
    print(f"2. Получены данные перевала")

    update_data = API_TEST_DATA.copy()
    update_data['title'] = 'Интеграционный тест'
    response = requests.patch(f"{BASE_URL}/submitData/{pereval_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()['state'] == 1
    print(f"3. Перевал обновлен")

    email = API_TEST_DATA['user']['email']
    response = requests.get(f"{BASE_URL}/submitData/", params={"user__email": email})
    assert response.status_code == 200
    data = response.json()
    assert data['count'] >= 1
    print(f"4. Найдено {data['count']} перевалов пользователя {email}")

    print("✓ Интеграционный тест пройден успешно")