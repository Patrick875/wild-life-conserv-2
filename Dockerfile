FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN python3 -m pip install --upgrade pip && python3 -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["sh","-c","python3 -m flask db upgrade && python3 -m database.seeders.seed && gunicorn -c gunicorn_config.py run:app --log-level debug"]