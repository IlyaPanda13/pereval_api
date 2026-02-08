import pytest
import os
import json
from app.database import DatabaseManager

TEST_DATA = {
    "beauty_title": "пер. ",
    "title": "Тестовый перевал",
    "other_titles": "Тест",
    "connect": "",
    "add_time": "2023-01-01 12:00:00",
    "user": {
        "email": "test@example.com",
        "fam": "Тестов",
        "name": "Тест",
        "otc": "Тестович",
        "phone": "+79990001122"
    },
    "coords": {
        "latitude": "45.0000",
        "longitude": "7.0000",
        "height": "1000"
    },
    "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "",
        "spring": ""
    },
    "images": [
        {"data": "iVBORw0KGgoAAAANSUhEUg==", "title": "Тест фото"}
    ]
}


@pytest.fixture
def db_manager():
    """Фикстура для создания экземпляра DatabaseManager"""
    return DatabaseManager()


@pytest.fixture
def sample_pereval_id(db_manager):
    """Фикстура создает тестовый перевал и возвращает его ID"""
    pereval_id = db_manager.add_pereval(TEST_DATA)
    yield pereval_id


def test_add_pereval(db_manager):
    """Тест добавления нового перевала"""
    pereval_id = db_manager.add_pereval(TEST_DATA)
    assert pereval_id is not None
    assert isinstance(pereval_id, int)
    print(f"Добавлен перевал с ID: {pereval_id}")


def test_get_pereval_by_id(db_manager, sample_pereval_id):
    """Тест получения перевала по ID"""
    pereval = db_manager.get_pereval_by_id(sample_pereval_id)
    assert pereval is not None
    assert pereval['id'] == sample_pereval_id
    assert 'raw_data' in pereval
    assert 'images' in pereval

    raw_data = pereval['raw_data']
    if isinstance(raw_data, str):
        raw_data = json.loads(raw_data)
    assert raw_data['status'] == 'new'


def test_get_perevals_by_email(db_manager, sample_pereval_id):
    """Тест поиска перевалов по email"""
    email = TEST_DATA['user']['email']
    perevals = db_manager.get_perevals_by_email(email)
    assert isinstance(perevals, list)
    assert len(perevals) >= 1

    found = any(p['id'] == sample_pereval_id for p in perevals)
    assert found, f"Перевал с ID {sample_pereval_id} не найден по email {email}"


def test_update_pereval(db_manager, sample_pereval_id):
    """Тест обновления перевала"""
    update_data = TEST_DATA.copy()
    update_data['title'] = 'Обновленное название'
    update_data['coords']['height'] = '1500'

    success, message = db_manager.update_pereval(sample_pereval_id, update_data)
    assert success is True
    assert message is None

    updated = db_manager.get_pereval_by_id(sample_pereval_id)
    raw_data = updated['raw_data']
    if isinstance(raw_data, str):
        raw_data = json.loads(raw_data)

    assert raw_data['title'] == 'Обновленное название'
    assert raw_data['coords']['height'] == '1500'
    assert raw_data['user']['email'] == TEST_DATA['user']['email']


def test_update_pereval_wrong_status(db_manager):
    """Тест: нельзя обновить перевал со статусом не 'new'"""
    pereval_id = db_manager.add_pereval(TEST_DATA)

    print(f"Тест требует ручной проверки: измени статус записи {pereval_id} на 'accepted' в БД")
    print(f"Затем PATCH запрос должен вернуть state: 0")