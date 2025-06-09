FROM bitnami/spark:3.5

USER root

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY amazon_spark_streaming_job.py .

CMD ["spark-submit", "--master", "spark://spark-master:7077", "amazon_spark_streaming_job.py"]