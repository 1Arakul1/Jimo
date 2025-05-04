## Установка

1.  **Клонируйте репозиторий (если применимо):**
    ```bash
    git clone <your_repository_url>
    cd <your_project_directory>
    ```

2.  **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # для Windows
    # source venv/bin/activate  # для Linux/macOS
    ```

3.  **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Настройте подключение к базе данных MS SQL Server:**
    *   Убедитесь, что у вас установлен MS SQL Server и настроен ODBC драйвер.
    *   Создайте файл `.env` в корневой папке проекта и укажите переменные окружения для подключения к базе данных (см. пример ниже).

5.  **Создайте базу данных:**
    ```bash
    python database_utils.py
    ```
    *   Этот скрипт создаст базу данных "Собачки" (или другую, указанную в `.env`) на вашем сервере MS SQL Server.

6.  **Примените миграции:**
    ```bash
    python manage.py migrate
    ```

7.  **Создайте суперпользователя:**
    ```bash
    python manage.py createsuperuser
    ```

8.  **Запустите сервер разработки:**
    ```bash
    python manage.py runserver