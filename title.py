#!/usr/bin/env python3

from html.parser import HTMLParser
from urllib.request import urlopen

class TitleParser(HTMLParser):
    
    def __init__(self, html):
        self.title = ''
        self.in_head = False
        self.read_data = False
        HTMLParser.__init__(self)
        self.feed(html)
    
    def handle_starttag(self, tag, attrs):
        if tag == 'head':
            self.in_head = True
        elif tag == 'title' and self.in_head and not self.title:
            self.read_data = True
    
    def handle_endtag(self, tag):
        if tag == 'head':
            self.in_head = False
        elif tag == 'title':
            self.read_data = False
    
    def handle_data(self, data):
        if self.read_data:
            self.title += data

def get_title(url):
    if not url.startswith('http://'):
        url = 'http://'+url
    html = urlopen(url).read().decode()
    return TitleParser(html).title

def main():
    from sys import argv
    print(get_title(argv[1]))

if __name__ == '__main__':
    main()
