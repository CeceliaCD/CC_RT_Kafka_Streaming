FROM bitnami/spark:3.5

WORKDIR /opt/app

COPY amazon_spark_streaming_job.py .

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["spark-submit", "--master", "spark://spark-master:7077", "amazon_spark_streaming_job.py"]