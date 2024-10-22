import requests
from prometheus_client import start_http_server, Gauge
import xml.etree.ElementTree as ET
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Define Prometheus metrics
class RTMPMetrics:
    def __init__(self):
        # Server metrics
        self.uptime = Gauge("rtmp_uptime_seconds", "RTMP Server uptime in seconds")
        self.connections_accepted = Gauge(
            "rtmp_connections_accepted_total", "Total accepted connections"
        )
        self.bandwidth_in = Gauge(
            "rtmp_bandwidth_in_bytes", "Incoming bandwidth in bytes/s"
        )
        self.bandwidth_out = Gauge(
            "rtmp_bandwidth_out_bytes", "Outgoing bandwidth in bytes/s"
        )
        self.bytes_in = Gauge("rtmp_bytes_in_total", "Total incoming bytes")
        self.bytes_out = Gauge("rtmp_bytes_out_total", "Total outgoing bytes")

        # Stream metrics
        self.stream_bandwidth_in = Gauge(
            "rtmp_stream_bandwidth_in_bytes",
            "Stream incoming bandwidth in bytes/s",
            ["stream_name"],
        )
        self.stream_bandwidth_out = Gauge(
            "rtmp_stream_bandwidth_out_bytes",
            "Stream outgoing bandwidth in bytes/s",
            ["stream_name"],
        )
        self.stream_bandwidth_audio = Gauge(
            "rtmp_stream_bandwidth_audio_bytes",
            "Stream audio bandwidth in bytes/s",
            ["stream_name"],
        )
        self.stream_bandwidth_video = Gauge(
            "rtmp_stream_bandwidth_video_bytes",
            "Stream video bandwidth in bytes/s",
            ["stream_name"],
        )
        self.stream_clients = Gauge(
            "rtmp_stream_clients", "Number of clients per stream", ["stream_name"]
        )

        # Video metrics
        self.video_height = Gauge(
            "rtmp_video_height", "Video height in pixels", ["stream_name"]
        )
        self.video_width = Gauge(
            "rtmp_video_width", "Video width in pixels", ["stream_name"]
        )
        self.video_frame_rate = Gauge(
            "rtmp_video_frame_rate", "Video frame rate", ["stream_name"]
        )


class RTMPExporter:
    def __init__(self, rtmp_url, polling_interval_seconds=15):
        self.rtmp_url = rtmp_url
        self.polling_interval_seconds = polling_interval_seconds
        self.metrics = RTMPMetrics()

    def fetch_rtmp_stats(self):
        try:
            response = requests.get(self.rtmp_url)
            response.raise_for_status()
            return ET.fromstring(response.text)
        except requests.RequestException as e:
            logging.error(f"Error fetching RTMP stats: {e}")
            return None
        except ET.ParseError as e:
            logging.error(f"Error parsing XML: {e}")
            return None

    def update_metrics(self, xml_root):
        if xml_root is None:
            return

        # Update server metrics
        self.metrics.uptime.set(float(xml_root.find("uptime").text))
        self.metrics.connections_accepted.set(float(xml_root.find("naccepted").text))
        self.metrics.bandwidth_in.set(float(xml_root.find("bw_in").text))
        self.metrics.bandwidth_out.set(float(xml_root.find("bw_out").text))
        self.metrics.bytes_in.set(float(xml_root.find("bytes_in").text))
        self.metrics.bytes_out.set(float(xml_root.find("bytes_out").text))

        # Update stream metrics
        for stream in xml_root.findall(".//stream"):
            stream_name = stream.find("name").text

            # Stream bandwidth metrics
            if stream.find("bw_in") is not None:
                self.metrics.stream_bandwidth_in.labels(stream_name).set(
                    float(stream.find("bw_in").text)
                )
            if stream.find("bw_out") is not None:
                self.metrics.stream_bandwidth_out.labels(stream_name).set(
                    float(stream.find("bw_out").text)
                )
            if stream.find("bw_audio") is not None:
                self.metrics.stream_bandwidth_audio.labels(stream_name).set(
                    float(stream.find("bw_audio").text)
                )
            if stream.find("bw_video") is not None:
                self.metrics.stream_bandwidth_video.labels(stream_name).set(
                    float(stream.find("bw_video").text)
                )

            # Client count
            if stream.find("nclients") is not None:
                self.metrics.stream_clients.labels(stream_name).set(
                    float(stream.find("nclients").text)
                )

            # Video metadata
            meta = stream.find("meta/video")
            if meta is not None:
                if meta.find("width") is not None:
                    self.metrics.video_width.labels(stream_name).set(
                        float(meta.find("width").text)
                    )
                if meta.find("height") is not None:
                    self.metrics.video_height.labels(stream_name).set(
                        float(meta.find("height").text)
                    )
                if meta.find("frame_rate") is not None:
                    self.metrics.video_frame_rate.labels(stream_name).set(
                        float(meta.find("frame_rate").text)
                    )

    def run(self, port=9101):
        # Start Prometheus HTTP server
        start_http_server(port)
        logging.info(f"Prometheus exporter started on port {port}")

        while True:
            xml_stats = self.fetch_rtmp_stats()
            if xml_stats is not None:
                self.update_metrics(xml_stats)
                logging.info("Metrics updated successfully")
            time.sleep(self.polling_interval_seconds)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RTMP Prometheus Exporter")
    parser.add_argument(
        "--rtmp-url",
        default="http://streaming.convay.com/stat",
        help="URL to RTMP statistics XML (default: http://localhost/stat)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to expose Prometheus metrics (default: 9101)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Polling interval in seconds (default: 15)",
    )

    args = parser.parse_args()

    exporter = RTMPExporter(
        rtmp_url=args.rtmp_url, polling_interval_seconds=args.interval
    )

    try:
        exporter.run(port=args.port)
    except KeyboardInterrupt:
        logging.info("Exporter stopped by user")
