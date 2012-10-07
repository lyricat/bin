#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# filename: QQWry.py
'''QQWry 模块, 提供读取纯真IP数据库的数据的功能.

纯真数据库格式参考 http://lumaqq.linuxsir.org/article/qqwry_format_detail.html
作者 AutumnCat. 最后修改在 2008年 04月 29日
bones7456 最后修改于 2009-02-02
本程序遵循 GNU GENERAL PUBLIC LICENSE Version 2 (http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)
'''
#数据文件下载地址： http://update.cz88.net/soft/qqwry.rar
from struct import unpack, pack
import sys, _socket, mmap

DataFileName="/home/shellex/Static/QQWry.Dat"

def _ip2ulong(ip):
    '''点分十进制 -> unsigned long
    '''
    return unpack('>L', _socket.inet_aton(ip))[0]

def _ulong2ip(ip):
    '''unsigned long -> 点分十进制
    '''
    return _socket.inet_ntoa(pack('>L', ip))

class QQWryBase:
    '''QQWryBase 类, 提供基本查找功能.

    注意返回的国家和地区信息都是未解码的字符串, 对于简体版数据库应为GB编码, 对于繁体版则应为BIG5编码.
    '''
    class ipInfo(tuple):
        '''方便输出 ip 信息的类.

        ipInfo((sip, eip, country, area)) -> ipInfo object
        '''
        def __str__(self):
            '''str(x)
            '''
            return str(self[0]).ljust(16) + ' - ' + str(self[1]).rjust(16) + ' ' + self[2] + self[3]

        def normalize(self):
            '''转化ip地址成点分十进制.
            '''
            return QQWryBase.ipInfo((_ulong2ip(self[0]), _ulong2ip(self[1]), self[2], self[3]))

    def __init__(self, dbfile):
        '''QQWryBase(dbfile) -> QQWryBase object

        dbfile 是数据库文件的 file 对象.
        '''
        self.f = dbfile
        self.f.seek(0)
        self.indexBaseOffset = unpack('<L', self.f.read(4))[0] #索引区基址
        self.Count = (unpack('<L', self.f.read(4))[0] - self.indexBaseOffset) / 7 # 索引数-1

    def Lookup(self, ip):
        '''x.Lookup(ip) -> (sip, eip, country, area) 查找 ip 所对应的位置.

        ip, sip, eip 是点分十进制记录的 ip 字符串.
        sip, eip 分别是 ip 所在 ip 段的起始 ip 与结束 ip.
        '''
        return self.nLookup(_ip2ulong(ip))

    def nLookup(self, ip):
        '''x.nLookup(ip) -> (sip, eip, country, area) 查找 ip 所对应的位置.

        ip 是 unsigned long 型 ip 地址.
        其它同 x.Lookup(ip).
        '''
        si = 0
        ei = self.Count
        if ip < self._readIndex(si)[0]:
            raise StandardError('IP NOT Found.')
        elif ip >= self._readIndex(ei)[0]:
            si = ei
        else: # keep si <= ip < ei
            while (si + 1) < ei:
                mi = (si + ei) // 2
                if self._readIndex(mi)[0] <= ip:
                    si = mi
                else:
                    ei = mi
        ipinfo = self[si]
        if ip > ipinfo[1]:
            raise StandardError('IP NOT Found.')
        else:
            return ipinfo

    def __str__(self):
        '''str(x)
        '''
        tmp = []
        tmp.append('RecCount:')
        tmp.append(str(len(self)))
        tmp.append('\nVersion:')
        tmp.extend(self[self.Count].normalize()[2:])
        return ''.join(tmp)

    def __len__(self):
        '''len(x)
        '''
        return self.Count + 1

    def __getitem__(self, key):
        '''x[key]

        若 key 为整数, 则返回第key条记录(从0算起, 注意与 x.nLookup(ip) 不一样).
        若 key 为点分十进制的 ip 描述串, 同 x.Lookup(key).
        '''
        if type(key) == type(0):
            if (key >=0) and (key <= self.Count):
                index = self._readIndex(key)
                sip = index[0]
                self.f.seek(index[1])
                eip = unpack('<L', self.f.read(4))[0]
                (country,area) = self._readRec()
                return QQWryBase.ipInfo((sip, eip, country, area))
            else:
                raise KeyError('INDEX OUT OF RANGE.')
        elif type(key) == type(''):
            try:
                return self.Lookup(key).normalize()
            except StandardError, e:
                if e.message == 'IP NOT Found.':
                    raise KeyError('IP NOT Found.')
                else:
                    raise e
        else:
            raise TypeError('WRONG KEY TYPE.')

    def __iter__(self):
        '''返回迭代器(生成器).
        '''
        for i in range(0, len(self)):
            yield self[i]

    def _read3ByteOffset(self):
        '''_read3ByteOffset() -> unsigned long 从文件 f 读入长度为3字节的偏移.
        '''
        return unpack('<L', self.f.read(3) + '\x00')[0]

    def _readCStr(self):
        '''x._readCStr() -> string 读 '\0' 结尾的字符串.
        '''
        if self.f.tell() == 0:
            return 'Unknown'
        tmp = []
        ch = self.f.read(1)
        while ch != '\x00':
            tmp.append(ch)
            ch = self.f.read(1)
        return ''.join(tmp)

    def _readIndex(self, n):
        '''x._readIndex(n) -> (ip ,offset) 读取第n条索引.
        '''
        self.f.seek(self.indexBaseOffset + 7 * n)
        return unpack('<LL', self.f.read(7) + '\x00')

    def _readRec(self, onlyOne=False):
        '''x._readRec() -> (country, area) 读取记录的信息.
        '''
        mode = unpack('B', self.f.read(1))[0]
        if mode == 0x01:
            rp = self._read3ByteOffset()
            bp = self.f.tell()
            self.f.seek(rp)
            result = self._readRec(onlyOne)
            self.f.seek(bp)
            return result
        elif mode == 0x02:
            rp = self._read3ByteOffset()
            bp = self.f.tell()
            self.f.seek(rp)
            result = self._readRec(True)
            self.f.seek(bp)
            if not onlyOne:
                result.append(self._readRec(True)[0])
            return result
        else: # string
            self.f.seek(-1,1)
            result = [self._readCStr()]
            if not onlyOne:
                result.append(self._readRec(True)[0])
            return result
    pass # End of class QQWryBase

class QQWry(QQWryBase):
    '''QQWry 类.
    '''
    def __init__(self, filename='QQWry.Dat'):
        '''QQWry(filename) -> QQWry object

        filename 是数据库文件名.
        '''
        f = open(filename, 'rb')
        QQWryBase.__init__(self, f)

class MQQWry(QQWryBase):
    '''MQQWry 类.

    将数据库放到内存的 QQWry 类.
    查询速度大约快两倍.
    '''
    def __init__(self, filename=DataFileName, dbfile=None):
        '''MQQWry(filename[,dbfile]) -> MQQWry object

        filename 是数据库文件名.
        也可以直接提供 dbfile 文件对象. 此时 filename 被忽略.
        '''
        if dbfile == None:
            try:
                dbf = open(filename, 'rb')
            except IOError:
                print "ERROR:",filename,"is not exist!"
                sys.exit(1)
        else:
            dbf = dbfile
        bp = dbf.tell()
        dbf.seek(0)
        QQWryBase.__init__(self, mmap.mmap(dbf.fileno(), 0, access = 1))
        dbf.seek(bp)

    def _readCStr(self):
        '''x._readCStr() -> string 读 '\0' 结尾的字符串.
        '''
        pstart = self.f.tell()
        if pstart == 0:
            return 'Unknown'
        else:
            pend = self.f.find('\x00', pstart)
            if pend < 0:
                raise StandardError('Fail To Read CStr.')
            else:
                self.f.seek(pend + 1)
                return self.f[pstart:pend].decode('GBK').encode('UTF-8')

    def _readIndex(self, n):
        '''x._readIndex(n) -> (ip ,offset) 读取第n条索引.
        '''
        startp = self.indexBaseOffset + 7 * n
        return unpack('<LL', self.f[startp:startp + 7] + '\x00')

if __name__ == '__main__':
    try:
        Q = MQQWry() # 数据库文件名为 ./QQWry.Dat
        if len(sys.argv) == 1:
            print Q
        if len(sys.argv) == 2:
            if sys.argv[1]=='-': #参数只有一个“-”时，从标准输入读取IP
                print ''.join(Q[raw_input()][2:])
            elif sys.argv[1] in ('all','-a','-all'): #遍历示例代码
                for i in Q:
                    print i.normalize()
            else: #参数只有一个IP时，只输出简要的信息
                print ''.join(Q[sys.argv[1]][2:])
        else:
            for i in sys.argv[1:]:
                print Q[i]
    except StandardError, e:
        if e.message != '':
            print e.message
        else:
            raise e
    finally:
        pass
