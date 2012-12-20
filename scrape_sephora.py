from bs4 import BeautifulSoup
import urllib2
import re
import datetime
import json

__author__ = 'ecnalyr'

#  If we install pip and lxml correctly (gcc issues)
#  This will allow us to use something that isn't a regular expression
def soupify(htmlData):
    """Expects HTML data from a web page"""
    return BeautifulSoup(htmlData, "html.parser")


def getHtml(url):
    """Returns html data from a given url"""
    return urllib2.urlopen(url)


def stripTags(item):
    """Uses regex to remove xml tags from something
    that can be turned into a string"""
    stringVersion = str(item)
    return re.sub('<[^>]*>', '', stringVersion)  # i.e. <loc>


def stripExtraSpaces(item):
    """Uses regex to remove extra spaces from something
    that can be turned into a string"""
    stringVersion = str(item)
    return re.sub('  ', '', stringVersion)


def stripNewLines(item):
    """Uses regex to remove new lines from something
    that can be turned into a string"""
    stringVersion = str(item)
    return re.sub('\n', ' ', stringVersion)


def getPriceFromLink(link):
    """Expects a string link to a sephora.com product page"""
    soup = soupify(getHtml(link))
    try:
        price = soup.find("span", {"class": "price"}).string
        return price
    except AttributeError:
        return "There is no price"


def getPriceFromDiv(div):
    """Currently only returns FIRST PRICE - this is not the intended behavior
    Expects a BeautifulSoup div from sephora.com new product page"""
    try:
        price = div.find("span", {"class": "price"}).string
        return price
    except AttributeError:
        return "There is no price"


def getBrandAndNameFromDiv(div):
    """Expects a BeautifulSoup div from sephora.com new product page"""
    try:
        brand = div.find("span", {"class": "name OneLinkNoTx"})
        return stripTags(stripExtraSpaces(stripNewLines(brand))).lstrip()
    except AttributeError:
        return "There is no brand"


def getLinkFromDiv(div):
    """Expects a BeautifulSoup div from sephora.com new product page"""
    try:
        return div.find('a', {'class': 'product-image'})['href']
    except AttributeError:
        return "There is no link"

def getImageLinkFromDiv(div):
    """Expects a BeautifulSoup div from sephora.com new product page"""
    try:
        return div.find('a', {'class': 'product-image'}).find('img')['src']
    except AttributeError:
        return "There is no image link"

def prependSephoraRoot(link):
    """Expects the suffix of a Sephora.com link"""
    return "http://www.sephora.com" + link

def getSkuFromlink(link):
    """Expects the suffix of a Sephora.com product link"""
    return re.search('P\d{6}', link).group(0)  # i.e. P123456

def buildJsonPostRequest(url):
    '''expects a url to a .json post action'''
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'application/json')
    return request

class SephoraProduct:
    """A product from Sephora crated using a newItemDiv in a BeautifulSoup format"""
    def __init__(self, newItemDiv):
        self.price = str(getPriceFromDiv(newItemDiv))
        self.brandAndName = str(getBrandAndNameFromDiv(newItemDiv))
        self.timeAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.link = str(prependSephoraRoot(getLinkFromDiv(newItemDiv)))
        self.imageLink = str(prependSephoraRoot(getImageLinkFromDiv(newItemDiv)))
        self.sku = str(getSkuFromlink(self.link))
        self.json = json.dumps({'store':'Sephora', 'name':self.brandAndName, 'price':self.price, 'sku':self.sku, 
                                'link':self.link, 'imageLink':self.imageLink, 'scrape_time':self.timeAdded})

    def getPrice(self):
        return self.price

    def getBrandAndName(self):
        return self.brandAndName

    def getTimeAdded(self):
        return self.timeAdded

    def getLink(self):
        return self.link

    def getImageLink(self):
        return self.imageLink

    def getSku(self):
        '''Note that this is different than Sephora's item numbers'''
        return self.sku

    def getJson(self):
        return self.json

uploadProductsUrl = "http://0.0.0.0:3000/products.json"
sephoraNewItemLink = "http://www.sephora.com/contentStore/mediaContentTemplate.jsp?mediaId=12800020"
newItemSoup = soupify(getHtml(sephoraNewItemLink))
newItems = newItemSoup.find_all("div", {"class": "product-item"})

productList = []
for item in newItems:
    product = SephoraProduct(item)
    productList.append(product)

for item in productList[0:]:
    print str(item.getTimeAdded()) + " " + str(item.getPrice()) + " " + str(item.getBrandAndName())
    print item.getLink()
    print item.getImageLink()
    print item.getSku()
    jsonData = item.getJson()
    print jsonData
    print "******"
    request = buildJsonPostRequest(uploadProductsUrl)
    urllib2.urlopen(request, jsonData)
