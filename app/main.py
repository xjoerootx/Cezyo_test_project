"""Основной модуль приложения Catalog API.

Инициирует создание базы данных, FastAPI и подключает маршруты для работы
с каталогом, товарами и свойствами.
"""

from fastapi import FastAPI

from app.routers import catalog, product, properties
from app.seed_data import load_seed_data

load_seed_data()

app = FastAPI(title='Catalog API')

app.include_router(catalog.router)
app.include_router(product.router)
app.include_router(properties.router)
