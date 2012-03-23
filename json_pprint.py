#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
'''漂亮格式化输出 json
@author: Jiahua Huang <jhuangjiahua@gmail.com>
@license: LGPLv3+
@see: json
'''

import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def main():
    if sys.argv[1:] and os.path.exists(sys.argv[1]):
        s = file(sys.argv[1]).read()
        pass
    else:
        s = sys.stdin.read()
        pass
    if s:
        obj = json.loads(s)
        print json.dumps(obj, ensure_ascii=0, indent=4)
        pass
    pass

if __name__=="__main__":
    main()


