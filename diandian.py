# -*- coding: utf-8 -*-

import socket
socket.setdefaulttimeout(120)
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup as soup
import urlparse
from os import path as ospath
from os import mkdir
import sys

ua = 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20100101 Firefox/15.0'

class Fetch():
    def __init__(self):
        self.storePath = ''
        self.url = ''
        self.host = ''
        self.data = 'lite=1&month='
        self.dtype = 0

        self.monthes = []
        self.links = []
        self.imgs = []
        self.downloaded = 0

    def getDom(self, url, host, data):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        opener.addheaders = [('User-Agent', ua), ('Host', host)]
        urllib2.install_opener(opener)
        try:
            response = urllib2.urlopen(url, data, timeout=120)
            result = response.read()
        except:
            try:
                response = urllib2.urlopen(url, data, timeout=120)
                result = response.read()
            except:
                return False
        return soup(result)

    def _download(self, url, path):
        self.console('downloading ' + ospath.basename(url) + ' to ' + ospath.dirname(path) + ' ...')
        try:
            urllib.urlretrieve(url, path)
            self.downloaded = self.downloaded + 1
            self.console('done')
        except:
            try:
                urllib.urlretrieve(url, path)
                self.downloaded = self.downloaded + 1
                self.console('done')
            except:
                self.console('error')

    def console(self, str):
        print str

    def mkthedir(self):
        if not ospath.exists(self.storePath + self.host + ospath.sep):
            mkdir(self.storePath + self.host + ospath.sep)

    def setUrl(self, url):
        if url == '':
            return False
        if not url.startswith('http'):
            url = 'http://' + url
        self.host = urlparse.urlparse(url).netloc
        self.url = 'http://' + self.host + '/archive'
        self.ourl = url
        return True
    
    def getUrl(self):
        url = raw_input('input the blog or the archive url: ').strip()
        if url == '':
            self.console('you must input an url, e.g. http://justbeauty.diandian.com')
            self.getUrl()
            return None
        self.setUrl(url)
    
    def setStorePath(self, path):
        self.storePath = ospath.abspath(path) + ospath.sep
        if not ospath.exists(self.storePath):
            return False
        return True
    
    def getStorePath(self):
        self.storePath = raw_input('input the full path where you want to store the images: ')
        self.storePath = ospath.abspath(self.storePath) + ospath.sep
        if not ospath.exists(self.storePath):
            self.console('the path you input dose not exsit')
            self.getStorePath()
            
    def setDmethod(self, type):
        self.dtype = type
        if self.dtype != '1' and self.dtype != '2':
            return False
        return True

    def getDmethod(self):
        self.dtype = raw_input('choose download type(1 - download all images in the blog; 2 - download images in one archive): ')
        if self.dtype != '1' and self.dtype != '2':
            self.console('you can only input \'1\' or \'2\'')
            self.getDmethod()

    def getAllLinks(self):
        for m in self.monthes:
            self.console('finding archives of ' + m + ' ...')
            dom = self.getDom(self.url, self.host, self.data + m)
            if dom == False:
                self.console('open ' + self.url +' error')
                continue
            links = dom('a', 'post-meta')
            for l in links:
                self.links.append(l['href'])

        self.console('found ' + str(len(self.links)) + ' archives')

    def getMonthes(self):
        self.console('finding monthes ...')

        dom = self.getDom(self.url, self.host, None)
        if dom == False:
            self.console('open ' + self.url + ' error')
            return None
        monthes = dom.findAll('a', 'month')
        for m in monthes:
            self.monthes.append(m['data-month'])

        self.console('found ' + str(len(self.monthes)) + ' monthes')

    def getImgs(self):
        for l in self.links:
            self.console('finding images from ' + l + ' ...')
            dom = self.getDom(l, self.host, None)
            if dom == False:
                self.console('error')
                continue
            imgs = dom('img')
            for img in imgs:
                try:
                    a = img['src']
                except:
                    continue
                if a.find('img.libdd.com') == -1:
                    continue
                ws = a.split('_')
                w = int(ws[1])
                if w <= 200:
                    continue
                aas = a.split('/')
                name = aas[len(aas) - 1]
                self.imgs.append((name, a))
                self._download(a, self.storePath + self.host + '\\' + name)

        self.console('found ' + str(len(self.imgs)) + ' images and ' + str(self.downloaded) + ' were downloaded successfully')

    def download(self):
        for img in self.imgs:
            name = img[0]
            src = img[1]
            path = self.storePath + self.host + '\\' + name
            self._download(src, path)
        self.console('found ' + str(len(self.imgs)) + ' images and ' + str(self.downloaded) + ' were downloaded successfully')

    def _start(self):
        self.mkthedir()
        if self.dtype == '1':
            self.getMonthes()
            self.getAllLinks()
            self.getImgs()
        if self.dtype == '2':
            self.links = [self.ourl]
            self.getImgs()

    def done(self):
        self.monthes = []
        self.links = []
        self.imgs = []
        self.downloaded = 0

    def start(self):   
        self.getDmethod()
        self.getUrl()
        self.getStorePath()
        self._start()
        
    def usage(self):
        self.console('''
 Usage: python diandian.py [download type] [blog or archive url] [save path]
 [download type]: 1 - download all images in the blog; 2 - download images in one archive
 e.g: python diandian.py 1 justbeauty.diandian.com D:\\temp\\test
        ''')

if __name__ == '__main__':
    fetch = Fetch()
    if len(sys.argv) < 4:
        fetch.start()
    else:
        type = sys.argv[1] #下载类型
        url = sys.argv[2] #博客或文章地址
        path = sys.argv[3] #保存目录
        if fetch.setDmethod(type) and fetch.setUrl(url) and fetch.setStorePath(path):
            fetch._start()
        else:
            fetch.usage()
    
