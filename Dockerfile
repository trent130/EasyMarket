FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt test-requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r test-requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate --run-syncdb 2>/dev/null; daphne -b 0.0.0.0 -p 8000 students.asgi:application"]
