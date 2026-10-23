import httpx
import time
import random
from datetime import datetime

# --- НАСТРОЙКИ ---
# URL сервера Насти
BASE_URL = "http://localhost:4200"

# Данные для входа. Создадим этого пользователя, если его нет.
EMAIL = "terrarium_owner@example.com"
PASSWORD = "secure_password123"
FULL_NAME = "Владелец Террариума"

# Имя устройства, которое будем мониторить
DEVICE_NAME = "Террариум"


def register_user(client: httpx.Client):
    """Регистрирует пользователя, если он еще не создан."""
    print("[1] Попытка регистрации пользователя...")
    response = client.post(
        f"{BASE_URL}/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "full_name": FULL_NAME}
    )
    if response.status_code == 201:
        print("Пользователь успешно зарегистрирован.")
    elif response.status_code == 409:
        print("Пользователь уже существует, переходим ко входу.")
    else:
        print(f"Ошибка регистрации: {response.status_code} - {response.text}")
        exit(1)


def login_user(client: httpx.Client):
    """Выполняет вход и сохраняет cookies в клиенте."""
    print("[2] Попытка входа в систему...")
    response = client.post(
        f"{BASE_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        print("Вход выполнен успешно. Cookies получены.")
    else:
        print(f"Ошибка входа: {response.status_code} - {response.text}")
        exit(1)


def get_or_create_device(client: httpx.Client) -> str:
    """Ищет устройство по имени. Если не находит — создает новое."""
    print(f"[3] Поиск устройства '{DEVICE_NAME}'...")
    
    # Получаем список всех устройств пользователя
    response = client.get(f"{BASE_URL}/api/v1/devices/?limit=100")
    
    if response.status_code != 200:
        print(f"Ошибка получения списка устройств: {response.text}")
        exit(1)
        
    devices = response.json().get("data", [])
    
    # Ищем наше устройство
    for device in devices:
        if device.get("name") == DEVICE_NAME:
            print(f"Устройство найдено. ID: {device['id']}")
            return device["id"]

    # Если не нашли — создаем
    print("Устройство не найдено. Создаем новое...")
    device_data = {
        "name": DEVICE_NAME,
        "device_type": "термогигрометр",
        "location": "Комната с террариумом",
        "status": True,
        "description": "Виртуальный датчик температуры и влажности"
    }
    
    response = client.post(f"{BASE_URL}/api/v1/devices/", json=device_data)
    if response.status_code == 201:
        new_id = response.json()["id"]
        print(f"Устройство создано. ID: {new_id}")
        return new_id
    else:
        print(f"Ошибка создания устройства: {response.text}")
        exit(1)


def send_telemetry(client: httpx.Client, device_id: str):
    """Генерирует и отправляет данные на сервер."""
    # Генерируем случайные значения
    temp = round(random.uniform(24.0, 32.0), 1)
    humidity = round(random.uniform(60.0, 85.0), 1)
    
    # Формируем PATCH-запрос. 
    # Температуру пишем в поле value, влажность - в description
    payload = {
        "value": temp,
        "description": f"Влажность: {humidity}% (Обновлено: {datetime.now().strftime('%H:%M:%S')})"
    }
    
    response = client.patch(f"{BASE_URL}/api/v1/devices/{device_id}", json=payload)
    
    if response.status_code == 200:
        print(f"[OK] Телеметрия отправлена: T={temp}°C, H={humidity}%")
    else:
        print(f"[WARN] Ошибка отправки: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("=== ЗАПУСК СИМУЛЯТОРА ТЕРРАРИУМА ===")
    
    # Создаем клиент с сохранением cookies
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        
        # 1. Регистрация (если нужно)
        register_user(client)
        
        # 2. Логин (получение cookies)
        login_user(client)
        
        # 3. Получение или создание устройства
        device_id = get_or_create_device(client)
        
        # 4. Бесконечный цикл отправки данных
        print("\n=== МОНИТОРИНГ ЗАПУЩЕН (нажмите Ctrl+C для остановки) ===")
        try:
            while True:
                send_telemetry(client, device_id)
                time.sleep(10) # Ждем 10 секунд
        except KeyboardInterrupt:
            print("\nСимулятор остановлен пользователем.")