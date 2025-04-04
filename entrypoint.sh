#!/bin/bash
set -e

echo "Applying migrations..."
python manage.py migrate
echo "Migrations applied successfully."

exec gunicorn tradeoasis.wsgi:application --bind 0.0.0.0:8000