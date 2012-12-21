import datetime
import json
import urllib2
from scraper_tools import soupify, getHtml, buildJsonPostRequest

__author__ = 'ecnalyr'


uploadProductsUrl = "http://0.0.0.0:3000/products.json"
forever21NewItemLink = "http://www.forever21.com/Product/Category.aspx?br=f21&category=whatsnew_all&pagesize=100&page=1"
newItemSoup = soupify(getHtml(forever21NewItemLink))
newItems = newItemSoup.find_all("table", style="float: right")
productBaseUrl = "http://www.forever21.com/Product/Product.aspx?BR=f21&Category=whatsnew_all&ProductID="
# Can look for a table who's style is "height:300px;float: right" - this is a product
# each product table contains two trs: the first eventually contains the image, the second contains name/price
# The image can be found Product Table > first img tag src
# The brand can be found Product Table > second tr > div class="ItemTag2" gives the brand
# The name can be found Product Table > second tr > first <a> > div class="DisplayName"
# The price can be found Product Table > second tr > font class="price" - the price will have a dollar sign
# The SKU can be found Product Table > second tr > first input field's value="" < SKU will be there
# The link can be built with this format: "http://www.forever21.com/Product/Product.aspx?BR=f21&Category=whatsnew_all&ProductID=" + SKU
# Here's a product:
#<table border="0" height="300" style="float: right">
#<tr>
#<td align="center" class="td_col_b01" height="292" id="ctl00_MainContent_dlCategoryList_ctl00_tdImageColumn" valign="bottom"><div class="ItemImage"><a href="http://www.forever21.com/Product/Product.aspx?BR=f21&amp;Category=whatsnew_all&amp;ProductID=2051923777&amp;VariantID="><img border="0" id="image_2051923777" onerror="imgError(this);" onmouseout='fnChangeProductImageForMouseEvent(this, "http://www.forever21.com/images/main_cat/51923777-02.jpg");' onmouseover='fnChangeProductImageForMouseEvent(this, "http://www.forever21.com/images/main_cat/51923777-02.jpg");' src="http://www.forever21.com/images/main_cat/51923777-02.jpg"/></a><a class="play" href="javascript:showPopWin('/Product/product_pop.aspx?BR=f21&amp;Category=whatsnew_all&amp;ProductID=2051923777&amp;VariantID=',730,550,null,'center');"><img src="http://www.forever21.com/images/en/quickview/btn_quickview.png"/></a></div></td>
#</tr><tr>
#<td align="left" class="td_col_b01" height="90" id="ctl00_MainContent_dlCategoryList_ctl00_tdValueColumn" valign="top" width="199"><span id="ctl00_MainContent_dlCategoryList_ctl00_dvContainer"><div class="ItemTag1"><img src="http://www.forever21.com/images/en/tag/web_exclusive_199.gif"/></div><div class="ItemTag2">CAPSULE 2.1</div><a href="http://www.forever21.com/Product/Product.aspx?BR=f21&amp;Category=whatsnew_all&amp;ProductID=2051923777&amp;VariantID="><div class="DisplayName">Cross Stitch Maxi Skirt</div></a><font class="price">$29.80</font><br/><input id="ctl00_MainContent_dlCategoryList_ctl00_hdProductId" name="ctl00$MainContent$dlCategoryList$ctl00$hdProductId" type="hidden" value="2051923777"/><input id="ctl00_MainContent_dlCategoryList_ctl00_hdProductSKUId" name="ctl00$MainContent$dlCategoryList$ctl00$hdProductSKUId" type="hidden"/><input id="ctl00_MainContent_dlCategoryList_ctl00_hdColorCode" name="ctl00$MainContent$dlCategoryList$ctl00$hdColorCode" type="hidden"/></span></td>
#</tr>
#</table>

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
        return price
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
        self.timeAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.sku = str(getSkuFromTable(productTable))
        self.imageLink = str(getImageLinkFromTable(productTable))
        self.link = str(buildLinkFromSKU(self.sku))
        self.json = json.dumps({'store':'Forever 21', 'name':self.brandAndName, 'price':self.price, 'sku':self.sku,
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



productList = []
for item in newItems:
    product = Forever21Product(item)
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