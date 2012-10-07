#! /usr/bin/env python
# -*- coding:UTF-8 -*-

import urllib
import urllib2
import lxml
import lxml.html
import sys
import os
import os.path
import json

DEFAULT_BASE = '/home/shellex/Video/'
    
class Client(object):
    def __init__(self, base=DEFAULT_BASE):
        self.html = ''
        self.tmpfile = os.path.join(base, 'fetch.tmp')
        self.base = base
    
    def fetch(self, url):
        html = ''
        def _fetch(url):
            request =  urllib2.Request(url)
            return urllib2.urlopen(request).read()
        if os.path.exists(self.tmpfile):
            fd = open(self.tmpfile, 'r')
            if url == fd.readline()[:-1]:
                print 'Cache matched, use cached data'
                html = fd.read()
            else:
                html = _fetch(url)
            fd.close()
        else:
            html = _fetch(url) 
            if html:
                fd = open(self.tmpfile, 'w+')
                fd.write(url + '\n')
                fd.write(html)
                fd.close()
        return html

    def crack(self, data):
        videos = []
        meta = {'title': '', 'count': 0}
        doc = lxml.html.fromstring(data)
        meta['title'] = doc.xpath('//*/div[@class="m-cdes"]/h2')[0].text.encode('utf-8')
        for ri, tr in enumerate(doc.xpath('//*/table[@id="list2"]/tr')):
            title = ''
            link = ''
            tds =  tr.xpath('.//td')            
            if ri == 0:
                continue
            for di, td in enumerate(tds):
                if di == 0: # title
                    title = td.text.strip()
                    title += td.xpath('.//a')[0].text.strip()
                    title = title.encode('utf-8')
                elif di == 1: # link
                    link = td.xpath('.//a/@href')
                    if len(link) == 0:
                        print '#%d is not be translated yet.' % ri
                        continue
                    else:
                        link = link[0].strip()
            videos.append((title, link))
        meta['count'] = len(videos)
        return meta, videos

def writeMeta(base, meta):
    os.chdir(base)
    path = os.path.join(base, meta['title'])
    if not os.path.exists(path):
        os.mkdir(meta['title'])
    fd = open('%s/metadata.json' % path, 'w+')
    fd.write(json.dumps(meta))
    fd.close()
    return os.path.join(path, 'metadata.json')

def buildSh(base, meta, videos):
    os.chdir(base)
    path = os.path.join(base, meta['title'])
    if not os.path.exists(path):
        os.mkdir(meta['title'])
    fd = open('%s/fetch.sh' % path, 'w+')
    fd.write('#! /bin/sh\n')
    for t, l in videos:
        fd.write('aria2c -j 5 -s 5 -d "%s" -o "%s.mp4" "%s"\n' % (path, t, l))
    fd.close()
    return os.path.join(path, 'fetch.sh')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: %s url' % sys.argv[0]
        sys.exit(0) 
    url = sys.argv[1]
    if os.environ.has_key('OC_BASE'):
        base = os.environ['OC_BASE']
    else:
        base = DEFAULT_BASE
    cli = Client(base)
    print 'Fetch url:', url
    data = cli.fetch(url)
    print 'Analyze HTML'
    metadata, videos = cli.crack(data)
    print ' - Course Name:', metadata['title']
    print ' - Video Count:', metadata['count']
    print 'Write Metadata:', writeMeta(base, metadata)
    print 'Build download script:', buildSh(base, metadata, videos)



