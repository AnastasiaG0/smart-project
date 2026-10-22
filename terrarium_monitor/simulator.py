"""
Симулятор датчиков микроклимата террариума.
Генерирует случайные показания температуры и влажности.
"""
import random
import time
from datetime import datetime


def get_microclimate():
    """Возвращает эмуляцию показаний датчиков террариума"""
    return {
        "temperature": round(random.uniform(24.0, 32.0), 1),
        "humidity": round(random.uniform(60.0, 85.0), 1),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    print("Terrarium Monitor started")
    while True:
        data = get_microclimate()
        print(f"Sensor data: {data}")
        time.sleep(10)