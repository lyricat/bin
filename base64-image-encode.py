#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author: Huang Jiahua <jhuangjiahua@gmail.com>
# Last modified: 

import base64
import sys

def imgdobase64(str1):
	#strs='<img src="data:image/png;base64,\n'
	strs='<img src="data:image;base64,\n'
	stre='" />'
	str64=base64.encodestring(str1)
	return ''.join((strs,str64,stre))

if __name__=="__main__":
	if len(sys.argv) == 1 :
		print imgdobase64(sys.stdin.read())
		sys.exit()
	cm1 = sys.argv[1]
	if cm1 == "" or cm1 == "-h" or cm1 == "--help":
		print "* Usage: img file"
		sys.exit() 
	print imgdobase64(open(sys.argv[1]).read())
	
