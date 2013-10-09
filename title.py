#!/usr/bin/env python3

from urllib.request import urlopen
from urllib.error import URLError
from re import search, DOTALL

pattern = r'<title>(.+)</title>'

def get_title(url):
    """Takes a URL as an argument. Returns False if URL is invalid or parser
    chokes on HTML, None if no title tags were found and the title of the
    specified page otherwise.
    """
    if not url.startswith('http://'):
        url = 'http://'+url
    try:
        html = urlopen(url).read().decode()
    except URLError:
        return False
    title = search(pattern, html, flags=DOTALL)
    if title is None:
        return None
    else:
        return title.group(1)


def main():
    from sys import argv
    print(get_title(argv[1]))

if __name__ == '__main__':
    main()
