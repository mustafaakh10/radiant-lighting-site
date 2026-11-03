FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings.prod
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libjpeg62-turbo libwebp7 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput --settings=config.settings.prod

RUN useradd --create-home app && mkdir -p /app/media && chown -R app /app/media
USER app
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"]
