#!/bin/sh

# with sourd
#mencoder tv:// -tv driver=v4l2:width=640:height=480:device=/dev/video0:forceaudio:adevice=/dev/dsp -ovc lavc -oac mp3lame -lameopts cbr:br=64:mode=3 -o out.avi

# sans sound
mencoder tv:// -tv driver=v4l2:width=640:height=480:device=/dev/video0 -nosound -ovc lavc -o out.avi

# png snapshot
# mplayer -vf screenshot -fps 15 tv:// -tv driver=v4l2:device=/dev/video0
