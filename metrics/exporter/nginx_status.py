import requests
from dataclasses import dataclass
import time
import os
from prometheus_client import start_http_server, Gauge


@dataclass
class NginxStats:
    active_connections: int
    accepts: int
    handled: int
    requests: int
    reading: int
    writing: int
    waiting: int


class NginxStatusCollector:
    def __init__(self, nginx_status_url: str):
        self.nginx_status_url = nginx_status_url
        # Define Prometheus metrics
        self.nginx_up = Gauge("nginx_status_up", "NGINX status up")
        self.active_connections = Gauge(
            "nginx_status_active_connections", "Number of active connections"
        )
        self.accepts = Gauge(
            "nginx_status_accepts_total", "Total number of accepted connections"
        )
        self.handled = Gauge(
            "nginx_status_handled_total", "Total number of handled connections"
        )
        self.requests = Gauge("nginx_status_requests_total", "Total number of requests")
        self.reading = Gauge("nginx_status_reading", "Number of connections reading")
        self.writing = Gauge("nginx_status_writing", "Number of connections writing")
        self.waiting = Gauge("nginx_status_waiting", "Number of connections waiting")

    def get_stats(self) -> NginxStats:
        try:
            response = requests.get(self.nginx_status_url)
            response.raise_for_status()
            return self._parse_nginx_status(response.text)
        except requests.RequestException as e:
            print(f"Error fetching NGINX stats: {e}")
            # Return zeros if we can't fetch stats
            return NginxStats(0, 0, 0, 0, 0, 0, 0)

    def _parse_nginx_status(self, status_text: str) -> NginxStats:
        lines = status_text.strip().split("\n")

        # Parse active connections
        active_connections = int(lines[0].split(":")[1].strip())

        # Parse accepts, handled, requests
        metrics = lines[2].strip().split()
        accepts, handled, requests = map(int, metrics)

        # Parse reading, writing, waiting
        last_line = lines[3].strip().split()
        reading = int(last_line[1])
        writing = int(last_line[3])
        waiting = int(last_line[5])

        return NginxStats(
            active_connections=active_connections,
            accepts=accepts,
            handled=handled,
            requests=requests,
            reading=reading,
            writing=writing,
            waiting=waiting,
        )

    def update_metrics(self):
        try:
            stats = self.get_stats()
            # Update all metrics
            self.nginx_up.set(1)
            self.active_connections.set(stats.active_connections)
            self.accepts.set(stats.accepts)
            self.handled.set(stats.handled)
            self.requests.set(stats.requests)
            self.reading.set(stats.reading)
            self.writing.set(stats.writing)
            self.waiting.set(stats.waiting)
        except Exception as e:
            print(f"Error updating metrics: {e}")
            self.nginx_up.set(0)


def main():
    # Get configuration from environment variables
    nginx_status_url = os.getenv("NGINX_STATUS_URL", "http://localhost:80/nginx_status")
    exporter_port = int(os.getenv("STATUS_EXPORTER_PORT", "9114"))
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "15"))

    # Initialize the collector
    collector = NginxStatusCollector(nginx_status_url)

    # Start up the server to expose the metrics
    start_http_server(exporter_port)
    print(f"Status exporter listening on port {exporter_port}")
    print(f"Collecting status metrics from {nginx_status_url}")

    # Update metrics periodically
    while True:
        collector.update_metrics()
        time.sleep(polling_interval_seconds)


if __name__ == "__main__":
    main()
