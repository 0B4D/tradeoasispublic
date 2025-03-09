FROM python:3.13.1-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a volume for SQLite database
VOLUME /app/data

# Run gunicorn
CMD gunicorn tradeoasis.wsgi:application --bind 0.0.0.0:$PORT