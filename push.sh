#raspivid -o - -t 0 -n -vf -w 480 -h 270 -fps 15|cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://[::]:8160/}' :demux=h264
sudo raspivid -o - -t 0 -w 640 -h 360 -fps 25|cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264
