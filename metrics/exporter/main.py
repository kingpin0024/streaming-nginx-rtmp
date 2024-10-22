import time
import requests
from prometheus_client import start_http_server, Gauge
import xml.etree.ElementTree as ET

# Define metrics
UPTIME = Gauge("rtmp_uptime_seconds", "Uptime of the RTMP server in seconds")
BYTES_IN = Gauge("rtmp_bytes_in", "Total bytes received by the RTMP server")
BYTES_OUT = Gauge("rtmp_bytes_out", "Total bytes sent by the RTMP server")
CLIENTS = Gauge("rtmp_clients_connected", "Number of connected clients")
STREAMS = Gauge("rtmp_streams_active", "Number of active streams")


# Function to fetch and parse RTMP stats
def fetch_rtmp_stats(url):
    response = requests.get(url)
    response.raise_for_status()
    return ET.fromstring(response.content)


def update_metrics(rtmp_url):
    try:
        root = fetch_rtmp_stats(rtmp_url)

        # Parse uptime
        uptime = int(root.find(".//uptime").text)
        UPTIME.set(uptime)

        # Parse bytes in/out
        bytes_in = int(root.find(".//bytes_in").text)
        bytes_out = int(root.find(".//bytes_out").text)
        BYTES_IN.set(bytes_in)
        BYTES_OUT.set(bytes_out)

        # Parse clients
        nclients = int(root.find(".//server/application/live/nclients").text)
        CLIENTS.set(nclients)

        # Since there are no streams in the provided XML, we set streams to 0
        STREAMS.set(0)  # Update this if streams are available in the future

    except Exception as e:
        print(f"Error fetching RTMP stats: {e}")
        print(
            f"Response content: {ET.tostring(root, encoding='utf-8').decode('utf-8') if root is not None else 'No response'}"
        )


if __name__ == "__main__":
    # RTMP stats URL
    rtmp_url = "https://streaming.convay.com/stat"

    # Start Prometheus HTTP server
    start_http_server(8000)

    # Main loop to update metrics
    while True:
        update_metrics(rtmp_url)
        time.sleep(10)  # Update every 10 seconds
