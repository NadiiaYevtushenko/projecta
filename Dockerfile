# Використовуємо офіційний образ Python з Docker Hub
FROM python:3.11-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файл залежностей
COPY requirements.txt /app/

# Встановлюємо залежності
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копіюємо увесь код в контейнер
COPY . /app/

# Виставляємо порт 8000
EXPOSE 8000

# Команда для запуску Django сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
