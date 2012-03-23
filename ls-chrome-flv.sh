#!/bin/sh
# ~/bin/ls-chrome-flv.sh
# 列出 chrome gcflashplayer 下载的 flv 影片文件

GDIR=~/.cache/google-chrome/Default/Cache
cd $GDIR
file `ls -S | head -70` | grep -i Video | cut -d: -f1 | while read i ; do
    ls -lh "$PWD/$i"
done

