FROM python:3.13.1-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

COPY entrypoint.sh . 
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
