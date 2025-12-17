# asgi.py
import os
import sys

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import app
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Создаем ASGI-приложение
asgi_app = app

# Функция для запуска через Hypercorn
async def run_hypercorn():
    config = Config()
    config.bind = ["127.0.0.1:5000"]
    config.workers = 1
    config.accesslog = "-"
    config.errorlog = "-"
    config.loglevel = "info"
    config.server_names = ["SecureWebServer"]
    
    await serve(asgi_app, config)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_hypercorn())