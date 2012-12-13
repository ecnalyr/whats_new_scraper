from bs4 import BeautifulSoup
import urllib2
import re
import datetime

#  Need to install pip and lxml correctly (gcc issues)
#  This will allow us to use something that isn't a regular expression
def soupify(htmlData):
    '''Expects HTML data from a web page'''
    return BeautifulSoup(htmlData, "html.parser")

def getHtml(url):
    '''Returns html data from a given url'''
    return urllib2.urlopen(url)

def stripTags(item):
    '''Uses regex to remove xml tags from something'''
    '''that can be turned into a string'''
    stringVersion = str(item)
    return re.sub('<[^>]*>', '', stringVersion) #i.e. <loc>

def stripExtraSpaces(item):
    '''Uses regex to remove extra spaces from something'''
    '''that can be turned into a string'''
    stringVersion = str(item)
    return re.sub('  ', '', stringVersion)

def stripNewLines(item):
    '''Uses regex to remove new lines from something'''
    '''that can be turned into a string'''
    stringVersion = str(item)
    return re.sub('\n', ' ', stringVersion)

def getPriceFromLink(link):
    '''Expects a string link to a sephora.com product page'''
    # make the html into soup
    # look for a span with the class of "price"
    # extract the value from the above span
    soup = soupify(getHtml(link))
    try:
        price = soup.find("span", {"class": "price"}).string
        return price
    except AttributeError:
        return "There is no price"

def getPriceFromDiv(div):
    '''Currently only returns FIRST PRICE - this is not the intended behavior'''
    # '''Currently only returns FIRST PRICE - this is not the intended behavior'''
    '''Expects a BeautifulSoup div from sephora.com new product page'''
    # make the html into soup
    # look for a span with the class of "price"
    # extract the value from the above span
    try:
        price = div.find("span", {"class": "price"}).string
        return price
    except AttributeError:
        return "There is no price"

def getBrandFromDiv(div):
    '''Expects a BeautifulSoup div from sephora.com new product page'''
    try:
        brand = div.find("span", {"class": "name OneLinkNoTx"})
        return stripTags(stripExtraSpaces(stripNewLines(brand))).lstrip()
    except AttributeError:
        return "There is no brand"

### ORIGINAL
#actually gets xml
# sephoraLinksXml = getHtml("http://www.sephora.com/products-sitemap.xml") 

# sephoraLinksSoup = soupify(sephoraLinksXml)

# links = sephoraLinksSoup.find_all('loc')

# for item in links[:7]:
#     timeAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#     linkString = stripTags(item)
#     currentPrice = getPriceFromLink(linkString)
#     print str(timeAdded) + " " + currentPrice + " " + linkString

# print len(links)
### END ORIGINAL
sephoraNewItemLink = "http://www.sephora.com/contentStore/mediaContentTemplate.jsp?mediaId=12800020"
newItemSoup = soupify(getHtml(sephoraNewItemLink))
newItems = newItemSoup.find_all("div", {"class": "product-item"})
# look for each div with class="product-item"
    #getPriceFromDiv(div)
    # get the name of the product from span class="brand"
# for item in newItems:
#     timeAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
#     price = getPriceFromDiv(item)
#     brandAndName = getBrandFromDiv(item)
#     print str(timeAdded) + " " + str(price) + " " + str(brandAndName)


class SephoraProduct:
    '''A product from Sephora crated using a newItemDiv in a BeautifulSoup format'''
    def __init__(self, newItemDiv):
        self.price = str(getPriceFromDiv(newItemDiv))
        self.brandAndName = str(getBrandFromDiv(newItemDiv))
        self.timeAdded = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def getPrice(self):
        return self.price

    def getBrandAndName(self):
        return self.brandAndName

    def getTimeAdded(self):
        return self.timeAdded


productList = []
for item in newItems:
    product = SephoraProduct(item)
    productList.append(product)

for item in productList:
    print str(item.getTimeAdded()) + " " + str(item.getPrice()) + " " + str(item.getBrandAndName())
