FROM nginx:alpine AS frontend
RUN rm -rf /usr/share/nginx/html/*
COPY frontend/ /usr/share/nginx/html

FROM python:3.12-alpine AS supporting
WORKDIR /app
COPY backend/supporting/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/supporting/ .
CMD ["python", "app.py"]
