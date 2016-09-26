# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import re
from reppy.cache import RobotsCache
import traceback
import urllib
import tldextract
from urlparse import urlparse
from collections import namedtuple

def url_split(url):
    '''
    Simple helper function bringing together two different libraries for extracting
    a URLs components.
    In-putted URLs are somewhat validated, this is simply against a users adding
    example.com instead of http://example.com, the former will result in both
    parsers being incorrect.
    The results are then simply returned into a named tuple for easy extraction.
    '''
    # validate the url to see if user has added the http prefix
    if url.startswith('http'):
        url = url
    else:
        url = 'http://' + url

    # create objects for url parsers
    tld = tldextract.extract(url)  # parser from github that correctly extracts the sub / domain / tld
    o = urlparse(url)  # python standard lib parser

    protocol = o.scheme + '://'
    subdomain = tld.subdomain + '.' if tld.subdomain else ''
    domain = tld.domain + '.'
    tld = tld.suffix

    if o.query:
        path = o.path + '?' + o.query # domain path
    else:
        path = o.path  # domain path

    full = '{}{}{}{}{}'.format(protocol, subdomain, domain, tld, path)
    domain_and_tld = '{}{}'.format(domain, tld)

    Result = namedtuple(
        'urlsplit',
        ['protocol', 'subdomain', 'domain', 'tld', 'path', 'full', 'domain_and_tld']
        )  # Defining the namedtuple

    return Result(
        protocol=protocol,
        subdomain=subdomain,
        domain=domain,
        tld=tld,
        path=path,
        full=full,
        domain_and_tld=domain_and_tld
        )

def blocked_by_robots_txt(url):
    ''' returns bool for whether urls is blocked by 
    robots.txt or not. 
    '''
    robots = RobotsCache()
    return robots.allowed(url, 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')


def check_head_nofollow(soup):
    ''' checks to see if a page has a nofollow meta robots attribute
    '''
    try:
        meta = soup.findAll('meta', {'name':re.compile('robots', re.IGNORECASE)})[0]['content']
    except:
        meta = ''

    if 'nofollow' in meta.lower():
        return False
    else:
        return True
  

def check_head_noindex(soup):
    ''' checks to see if a page has a noindex meta robots attribute
    '''
    try:
        meta = soup.findAll('meta', {'name':re.compile('robots', re.IGNORECASE)})[0]['content']
    except:
        meta = ''
    if 'noindex' in meta.lower():
        return False
    else:
        return True

def check_page_header(r):
    ''' checks the headers for the x-robots-tag being set to noindex
    '''
    try:
        if 'noindex' in r.headers['x-robots-tag']:
            return False
    except:
        return True

def check_google_index(url):
    ''' does an info: search to see if url is indexed in google

    returns a bool.
    '''
    headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Encoding': 'gzip,deflate',
      'Accept-Language': 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4',
      'Cache-Control': 'no-cache',
      'Connection': 'close',
      'DNT': '1',
      'Pragma': 'no-cache',
      'Referrer' : 'http://www.google.co.uk',
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'
      }
    serp_status = requests.get('https://www.google.co.uk/search?q=info:{}'.format(url), proxies=False)
    data = serp_status.text
    soup = BeautifulSoup(data, 'html5lib')
    if soup.findAll('cite'):
        return True
    else:
        return False

def is_nofollow_on_link(bs4_link_obj):
    try:
        nofollow = bs4_link_obj['rel'][0]
        if nofollow == 'nofollow':
            return False
        else:
            return True
    except:
        return True

def is_noindex_on_link(bs4_link_obj):
    try:
        noindex = bs4_link_obj['rel'][0]
        if noindex == 'noindex':
            return False
        else:
            return True
    except:
        return True
		
def strip_trailing_slash(link):
    if link.endswith('/'):
        return link[:-1]
    else:
        return link

def check_canonical_matches(soup, link):
    ''' checks to see is the canonical tag matches the link
    checks both absolute and relative links.
    '''
    try:
        canonical = soup.find('link', {'rel':'canonical'})
        canonical_link = canonical['href']

        if strip_trailing_slash(canonical_link) == strip_trailing_slash(link) or strip_trailing_slash(canonical_link) == strip_trailing_slash(url_split(link).path):
            return True
        else:
            return False
    except:
        return True

def canonicall(soup, link):
    ''' checks to see is the canonical tag matches the link
    checks both absolute and relative links.
    '''
    try:
        canonical = soup.find('link', {'rel':'canonical'})
        canonical_link = canonical['href']

        return canonical_link
    except:
        return ''
