from prometheus_client import start_http_server, Gauge
from nginx_status import NginxStatusCollector
import time
import os

# Define Prometheus metrics
NGINX_UP = Gauge("nginx_up", "NGINX up status")
NGINX_ACTIVE_CONNECTIONS = Gauge(
    "nginx_active_connections", "Number of active connections"
)
NGINX_ACCEPTS = Gauge("nginx_accepts_total", "Total number of accepted connections")
NGINX_HANDLED = Gauge("nginx_handled_total", "Total number of handled connections")
NGINX_REQUESTS = Gauge("nginx_requests_total", "Total number of requests")
NGINX_READING = Gauge("nginx_reading", "Number of connections reading")
NGINX_WRITING = Gauge("nginx_writing", "Number of connections writing")
NGINX_WAITING = Gauge("nginx_waiting", "Number of connections waiting")


def update_metrics(collector: NginxStatusCollector):
    try:
        stats = collector.get_stats()

        # Update all metrics
        NGINX_UP.set(1)
        NGINX_ACTIVE_CONNECTIONS.set(stats.active_connections)
        NGINX_ACCEPTS.set(stats.accepts)
        NGINX_HANDLED.set(stats.handled)
        NGINX_REQUESTS.set(stats.requests)
        NGINX_READING.set(stats.reading)
        NGINX_WRITING.set(stats.writing)
        NGINX_WAITING.set(stats.waiting)
    except Exception as e:
        print(f"Error updating metrics: {e}")
        NGINX_UP.set(0)


def main():
    # Get configuration from environment variables
    nginx_status_url = os.getenv(
        "NGINX_STATUS_URL", "http://localhost:443/nginx_status"
    )
    exporter_port = int(os.getenv("EXPORTER_PORT", "9113"))
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "15"))

    # Initialize the collector
    collector = NginxStatusCollector(nginx_status_url)

    # Start up the server to expose the metrics
    start_http_server(exporter_port)
    print(f"Exporter listening on port {exporter_port}")
    print(f"Collecting metrics from {nginx_status_url}")

    # Update metrics periodically
    while True:
        update_metrics(collector)
        time.sleep(polling_interval_seconds)


if __name__ == "__main__":
    main()
