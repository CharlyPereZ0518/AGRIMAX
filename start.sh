#!/bin/bash
# Script de inicio para Railway que garantiza el uso correcto del puerto

PORT=${PORT:-8080}
echo "Iniciando Gunicorn en puerto: $PORT"
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
