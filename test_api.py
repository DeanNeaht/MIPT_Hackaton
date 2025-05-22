import requests
from datetime import datetime

API_URL = "http://localhost:8000/predict"

# Получаем текущую дату и время для теста
now = datetime.now()
date_str = now.strftime("%Y-%m-%d")
time_str = now.strftime("%H:%M:%S")

# Тестовые данные
test_data = {
    "utm_campaign": "blog",
    "device_category": "desktop",
    "device_os": "Windows",
    "device_brand": "Google",
    "device_browser": "Chrome",
    "geo_city": "Moscow",
    "visit_number": 2,
    "visit_date": date_str,
    "visit_time": time_str
}

# Отправляем запрос к API
try:
    response = requests.post(API_URL, json=test_data)
    
    # Проверяем статус ответа
    if response.status_code == 200:
        result = response.json()
        print(f"Вероятность совершения целевого действия: {result['probability']:.4f}")
        print(f"Предсказанный класс: {result['target_class']}")
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Ошибка при отправке запроса: {str(e)}") 