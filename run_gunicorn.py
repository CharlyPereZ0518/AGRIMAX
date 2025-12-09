import os
import sys

port = os.environ.get('PORT', '8080')
workers = os.environ.get('WEB_CONCURRENCY', '4')

print(f"Starting Gunicorn on port: {port} with {workers} workers")

cmd = f"gunicorn app:app --bind 0.0.0.0:{port} --workers {workers} --timeout 120 --access-logfile - --error-logfile -"
os.system(cmd)
