raspivid -o - -t 0 -n -vf -w 480 -h 270 -fps 15|cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8160/}' :demux=h264
