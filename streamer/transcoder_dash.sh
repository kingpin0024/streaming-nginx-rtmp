#!/bin/bash

# Wait for the RTMP server to become available
while ! nc -z rtmp 1935; do
  echo "Waiting for RTMP server..."
  sleep 5
done

# Ensure the output directory exists and has correct permissions
mkdir -p /var/www/html/dash
chmod 755 /var/www/html/dash

# Start FFmpeg transcoding for both 720p and 360p
exec ffmpeg -i rtmp://rtmp:1935/live/stream \
  -filter_complex "[v:0]split=2[v1][v2]; [v1]scale=-2:720[v720p]; [v2]scale=-2:360[v360p]" \
  -map "[v720p]" -c:v:0 libx264 -b:v:0 2800k \
  -map "[v360p]" -c:v:1 libx264 -b:v:1 1400k \
  -map a:0 -c:a aac -b:a 128k \
  -f dash \
  -init_seg_name "init_\$RepresentationID\$.m4s" \
  -media_seg_name "chunk_\$RepresentationID\$_\$Number%05d\$.m4s" \
  -use_template 1 \
  -use_timeline 1 \
  -seg_duration 4 \
  -streaming 1 \
  -window_size 5 \
  -adaptation_sets "id=0,streams=v id=1,streams=a" \
  -remove_at_exit 1 \
  "/var/www/html/dash/stream.mpd"
