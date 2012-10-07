#!/usr/bin/env python

import os
import sys
import time
import subprocess

base_dir = '/home/shellex'
src_dirs = [
     'Apps', 'Artwork', 'Desktop'
   , 'Dev', 'Documents', 'Ivory Tower'
   , 'Music', 'Pictures', 'Script'
   , 'Static', 'Templates', 'WWW']


def do_backup(src, dst, opts):
    if src[-1] == '/': src = src[:-1]
    backup_name = os.path.split(src)[1].replace(' ', '_')
    print 'Backup: %s to %s \t' % (src, dst) , 
    cmd = ['rsync', '--delete', '--progress', '-azvvrh', src, dst]
    proc = subprocess.Popen(cmd)
    proc.wait()
    if proc.returncode != 0:
        print '... Failed!'
    else:
        print '... OK!'
    return proc

def backup_dirs(dst):
    for src_dir in src_dirs:
        do_backup(os.path.join(base_dir, src_dir), dst, None)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: %s <dst path>' % sys.argv[0]
        sys.exit(0)
    if not os.path.exists(sys.argv[1]):
        print '"%s" is not exists, create it.' % sys.argv[1]
        os.mkdir(sys.argv[1])
    backup_dirs(sys.argv[1])

