# Используем Python 3.8
FROM python:3.8-slim


# Установка рабочей директории
WORKDIR /app

# Копируем код
COPY ./backend /app/backend
COPY ./GET_DATA /app/GET_DATA   # ⬅️ вот это обязательно!

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Устанавливаем переменные среды
ENV PYTHONPATH=/app

# Запускаем сервер
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
