import requests
import json

BASE_URL = "http://localhost:8000"

# Тестовые данные
test_data = {
    "beauty_title": "пер. ",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2021-09-22 13:18:13",
    "user": {
        "email": "test_user@mail.ru",
        "fam": "Пупкин",
        "name": "Василий",
        "otc": "Иванович",
        "phone": "+7 555 55 55"
    },
    "coords": {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1200"
    },
    "level": {
        "winter": "",
        "summer": "1А",
        "autumn": "1А",
        "spring": ""
    },
    "images": [
        {"data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
         "title": "Седловина"}
    ]
}


def test_all():
    print("1. Добавляем новый перевал (POST /submitData)")
    response = requests.post(f"{BASE_URL}/submitData", json=test_data)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if result.get("status") == 200:
        pereval_id = result["id"]

        print(f"\n2. Получаем добавленный перевал (GET /submitData/{pereval_id})")
        response = requests.get(f"{BASE_URL}/submitData/{pereval_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Found: {len(response.text) > 2}")

        print(f"\n3. Пытаемся обновить (PATCH /submitData/{pereval_id})")
        update_data = test_data.copy()
        update_data["title"] = "Обновленное название"
        response = requests.patch(f"{BASE_URL}/submitData/{pereval_id}", json=update_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        print(f"\n4. Ищем по email (GET /submitData/?user__email=test_user@mail.ru)")
        response = requests.get(f"{BASE_URL}/submitData/", params={"user__email": "test_user@mail.ru"})
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Found {data['count']} records")

        if data["count"] > 0:
            print(f"   First record ID: {data['results'][0]['id']}")


if __name__ == "__main__":
    test_all()