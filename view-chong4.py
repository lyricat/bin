#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# Author: Huang Jiahua <jhuangjiahua@gmail.com>
# License: GNU LGPL
# Last modified:

"""查看 http://www.chong4.net/ 语录

bash 版本是:
    wget -q  -O- http://www.chong4.net/show01.php | iconv -f gbk -t utf8 | sed 's/<[^>]*>//g'  | sed '/^$/d' | sed -n '/提供的语录/,/来源链接/p'

"""
__revision__ = '0.1'

import urllib
import re

def main():
    s = urllib.urlopen('http://www.chong4.net/show01.php').read().decode('gb18030')
    src = re.findall(u'"(http://.*?)".*来源链接', s)
    txt = re.sub('<[^>]*>', '\n', s)
    txt = txt.replace('&nbsp;', ' ')
    txt = txt.replace('\r', '')
    txt = re.sub('[\n\r\t]+', '\n', txt)
    txt = re.sub('&#(\d{1,5});',lambda m:unichr(int(m.group(1))), txt)
    txt = re.findall(u'提供的语录([^\0]*)来源链接', txt)[0]
    print txt
    print src[0]

if __name__=="__main__":
	main()



