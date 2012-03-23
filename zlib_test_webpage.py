#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
'''测试网站是否使用压缩
@author: Jiahua Huang <jhuangjiahua@gmail.com>
@license: LGPLv3+
@see: 
'''

import sys
import urllib2
import cStringIO as stringIO
import zlib
import gzip

def decompress(ret):
    for func in [ 
            lambda ret: gzip.GzipFile(fileobj=stringIO.StringIO(ret)).read(),
            lambda ret: zlib.decompress(ret),
            str,
    ]:
        try:
            return func(ret)
        except:
            pass
        pass
    pass

def tes(uri):
    if ':' not in uri:
        uri = 'http://' + uri
        pass
    print 'URI: %s\n' % uri
    opener = urllib2.build_opener()
    opener.addheaders.append(('Accept-Encoding', 'deflate, gzip'))
    opener.addheaders.append(('User-Agent', 'Mozilla/5.0 (Linux; U; Android 2.2.1; en-us; MB525 Build/3.4.2-155) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'))
    o = opener.open(uri)
    ret = o.read()
    dret = decompress(ret)
    print ''.join(o.headers.headers)
    print 'Original-Length: %s' % len(dret)
    print 'Compressed-Length: %s' % len(ret)
    print 'Compressibility: %2.2f%%' % (len(ret) * 100.0 / len(dret))
    pass

def main():
    for uri in sys.argv[1:]:
        tes(uri)
        pass
    pass

if __name__=="__main__":
    main()
