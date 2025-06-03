from flask import Flask, requests, Response
from prometheus_client import Counter, generate_latest
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
#from collections import defaultdict

app = Flask(__name__)

amazon_shopping_streaming_event_counter = Counter('amazon_events_total', 'Total Amazon shopping events processed', ['topic'])

@app.route('/')
def index():
    return 'Kafka Streaming Flask Exporter'

@app.route('/process_event/<topic>')
def process_event(topic):
    amazon_shopping_streaming_event_counter.labels(topic=topic).inc()
    return f"Processed topic: {topic}"

#web server gateway interface
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)