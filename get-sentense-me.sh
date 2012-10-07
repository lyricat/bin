#! /bin/sh
wget http://sentense.me/  -O - -q |\
sed -n 's/.*"\([^"]*1680x1050[^"]*\.png\)".*/http:\/\/sentense.me\1/p'|\
wget -i - -P ~/Pictures/sentense.me/wallpapers -nc -q 

