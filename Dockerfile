FROM python:3.12-slim
LABEL authors="manuela"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["gunicorn", "text_shuffle.wsgi:application", "--bind", "0.0.0.0:8000"]
