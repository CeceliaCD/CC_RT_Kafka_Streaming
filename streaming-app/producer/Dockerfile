FROM python:3.11-slim
WORKDIR /app
COPY amazon_shopping_transaction_producer.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "amazon_shopping_transaction_producer.py"]