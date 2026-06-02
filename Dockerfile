from python:3.11-slim

workdir ./app

copy requirements.txt .

run pip install --no-cache-dir -r requirements.txt

copy . .

expose 4800

cmd ["gunicorn","-b","0.0.0.0:4800","run:app"]