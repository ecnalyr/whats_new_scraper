import json
import re
import urllib2
from scraper_tools import soupify, getHtml, buildJsonPostRequest

__author__ = 'ecnalyr'


def getImageLinkFromDiv(div):
    """Expects a BeautifulSoup div from ae.com's new product page"""
    try:
        fullSrc = div.find('img')['src']
        return fullSrc.replace("//", "http://") # removes the unnecessary // from the beginning of the string
    except AttributeError:
        return "There is no Image Link"

def getSkuFromDiv(div):
    """Expects a BeautifulSoup div from ae.com's new product page"""
    try:
        baseUrl = div.find('a')['href']
        baseSku = re.search('\productId=(\d+_\d+)', baseUrl).group(0)
        return baseSku.replace("productId=", "")
    except AttributeError:
        return "There is no Sku"


def encodeBrandNameToUTF8(brandAndName):
    return str(brandAndName.encode("utf-8"))


def getBrandAndNameFromDiv(div):
    """Expects a BeautifulSoup div from ae.com's new product page"""
    try:
        brandAndName = div.find('span', {'class': 'name'}).string
        return str(brandAndName)
    except UnicodeEncodeError:
        return encodeBrandNameToUTF8(brandAndName)
    #        return "unicode encode error"
    except AttributeError:
        return "There is no brand and / or name"

def getPriceFromDiv(div):
    """Expects a BeautifulSoup div from ae.com's new product page"""
    try:
        price = div.find('span', {'class': 'price'}).string
        return price.replace("$", "") # have to remove the dollar sign from the price
    except AttributeError:
        return "There is no price"


def buildLinkFromSKU(sku):
    """Expects a SKU representing a product at ae.com"""
    return productBaseUrl + sku


class aeFemaleProduct:
    """A product from AE crated using a newItemDiv in a BeautifulSoup format"""
    def __init__(self, productDiv):
        self.price = str(getPriceFromDiv(productDiv))
        self.brandAndName = str(getBrandAndNameFromDiv(productDiv))
        self.sku = str(getSkuFromDiv(productDiv))
        self.imageLink = str(getImageLinkFromDiv(productDiv))
        self.link = str(buildLinkFromSKU(self.sku))
        self.json = json.dumps({'store':"AE Women's", 'name':self.brandAndName, 'price':self.price, 'sku':self.sku,
                                'link':self.link, 'imageLink':self.imageLink})

    def getPrice(self):
        return self.price

    def getBrandAndName(self):
        return self.brandAndName

    def getLink(self):
        return self.link

    def getImageLink(self):
        return self.imageLink

    def getSku(self):
        '''Note that this is different than Forever 21's item numbers'''
        return self.sku

    def getJson(self):
        return self.json

uploadProductsUrl = "http://frozen-stream-7233.herokuapp.com//products.json"
aeFemaleNewItemLink = "http://www.ae.com/web/browse/category.jsp?catId=cat90040"
newItemSoup = soupify(getHtml(aeFemaleNewItemLink))
newItems = newItemSoup.find_all('div', {'class': 'sProd'})
productBaseUrl = "http://www.ae.com/web/browse/product.jsp?productId="

productList = []
for item in newItems:
    product = aeFemaleProduct(item)
    productList.append(product)

for item in productList[0:]:
    print str(item.getPrice()) + " " + str(item.getBrandAndName())
    print item.getLink()
    print item.getImageLink()
    print item.getSku()
    jsonData = item.getJson()
    print jsonData
    print "******"
    request = buildJsonPostRequest(uploadProductsUrl)
    urllib2.urlopen(request, jsonData)