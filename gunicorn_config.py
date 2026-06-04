import os

workers = int(os.getenv('GUNICORN_PROCESSES', 2))
threads = int(os.getenv('GUNICORN_THREADS', 4))

bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"

forwarded_allow_ips = '*'

# secure_scheme_headers = {'X-Forwarded-Proto': 'https'}
