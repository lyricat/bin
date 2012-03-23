#! /bin/sh
traceroute $* | awk -F"[()]" '{if($2~/[0-9\.]./){printf("%s |",$0);system("qqwry.py "$2);}else{print $0}}'
