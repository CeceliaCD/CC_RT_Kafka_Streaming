FROM python:3.11-slim

WORKDIR /app

COPY amazon_shopping_topics_to_prometheus.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Exposing Prometheus metrics on port 8000
EXPOSE 8000

CMD ["python", "amazon_shopping_topics_to_prometheus.py"]