#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
'''用 zlib.compress 压缩文件
@author: Jiahua Huang <jhuangjiahua@gmail.com>
@license: LGPLv3+
@see: 
'''

import os
import sys
import zlib

def compressfile(fn, level=9):
    i = file(fn).read()
    o = zlib.compress(i, level)
    file(fn + '.z', 'w').write(o)
    pass

def main():
    import re
    i = re.findall('\0-(\d)\0', '\0' + '\0'.join(sys.argv) + '\0')
    level = int(i[0]) if i else 9        
    for fn in sys.argv[1:]:
        if os.path.exists(fn):
            compressfile(fn, level)
            pass
        pass
    pass

if __name__=="__main__":
    main()


