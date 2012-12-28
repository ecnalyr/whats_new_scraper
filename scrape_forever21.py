import datetime
import json
import urllib2
from scraper_tools import soupify, getHtml, buildJsonPostRequest

__author__ = 'ecnalyr'


def getImageLinkFromTable(table):
    """Expects a BeautifulSoup table from forever21.com new product page"""
    try:
        return table.find("a").find('img')['src']
    except AttributeError:
        return "There is no Image Link"

def getSkuFromTable(table):
    """Expects a BeautifulSoup table from forever21.com new product page"""
    try:
        return table.find("input")["value"]
    except AttributeError:
        return "There is no Sku"


def encodeBrandNameToUTF8(brand, name):
    return str(brand.encode("utf-8")) + " " + str(name.encode("utf-8"))


def getBrandAndNameFromDiv(table):
    """Expects a BeautifulSoup table from forever21.com new product page"""
    try:
        brand = table.find("div", {"class": "ItemTag2"}).string
        name = table.find("div", {"class": "DisplayName"}).string
        return str(brand) + " " + str(name)
    except UnicodeEncodeError:
        return encodeBrandNameToUTF8(brand, name)
#        return "unicode encode error"
    except AttributeError:
        return "There is no brand"

def getPriceFromDiv(table):
    """Expects a BeautifulSoup table from forever21.com new product page"""
    try:
        price = table.find("font", {"class": "price"}).string
        return price.replace("$", "") # have to remove the dollar sign from the price
    except AttributeError:
        return "There is no price"


def buildLinkFromSKU(sku):
    """Expects a SKU representing a product at Forever21.com"""
    return productBaseUrl + sku


class Forever21Product:
    """A product from Sephora crated using a newItemDiv in a BeautifulSoup format"""
    def __init__(self, productTable):
        self.price = str(getPriceFromDiv(productTable))
        self.brandAndName = str(getBrandAndNameFromDiv(productTable))
        self.sku = str(getSkuFromTable(productTable))
        self.imageLink = str(getImageLinkFromTable(productTable))
        self.link = str(buildLinkFromSKU(self.sku))
        self.json = json.dumps({'store':'Forever 21', 'name':self.brandAndName, 'price':self.price, 'sku':self.sku,
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

uploadProductsUrl = "http://0.0.0.0:3000/products.json"
forever21NewItemLink = "http://www.forever21.com/Product/Category.aspx?br=f21&category=whatsnew_all&pagesize=100&page=1"
newItemSoup = soupify(getHtml(forever21NewItemLink))
newItems = newItemSoup.find_all("table", style="float: right")
productBaseUrl = "http://www.forever21.com/Product/Product.aspx?BR=f21&Category=whatsnew_all&ProductID="

productList = []
for item in newItems:
    product = Forever21Product(item)
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