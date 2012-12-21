import urllib2
from bs4 import BeautifulSoup

__author__ = 'ecnalyr'

#  If we install pip and lxml correctly (gcc issues)
#  This will allow us to use something that isn't a regular expression
def soupify(htmlData):
    """Expects HTML data from a web page"""
    return BeautifulSoup(htmlData, "html.parser")


def getHtml(url):
    """Returns html data from a given url"""
    return urllib2.urlopen(url)


def buildJsonPostRequest(url):
    '''expects a url to a .json post action'''
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    return request