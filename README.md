1. **Клонируйте репозиторий и перейдите в его директорию:**

   ```git clone <URL-репозитория>```
   ```cd <имя-проекта>```

2. **Установите все необходимые зависимости:**

    ```pip install -r requirements.txt```

3. **Создайте файл ".env" и передайте в него существующие локальные параметры для подключения к БД "DATABASE_URL"**

4. **Запустите локальный сервер с помощью uvicorn:**

    ```uvicorn main:app --reload```

    Сервер будет доступен по адресу http://127.0.0.1:8000, при этом тестовые данные автоматически заполнят БД.

5. **Для тестирования эндпоинтов через Swagger перейдите по адресу http://127.0.0.1:8000/docs**
