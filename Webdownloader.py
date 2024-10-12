import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

whitelistTags = ["[gb]", "instock"]
blacklistTags = ["closed", "completed", "complete", "cancelled"]

def scrapePage(url):
    savePage(url, "index", "")
    f = open("index.html", "r")
    indexPage = BeautifulSoup(f, "html.parser")
    for post in indexPage.find_all("td"):
        if post.get('class')[0] != "subject" or post.get('class')[1] != "windowbg2":
            continue
        for postA in post.find_all("a"):
            link = postA.get("href")
            if str(link).find("profile") != -1:
                continue
            text = postA.contents[0]
            text = text.lower()
            for tag in blacklistTags:
                if text.find(tag) != -1:
                    continue
            tag_found = False
            for tag in whitelistTags:
                if text.find(tag) != -1:
                    tag_found = True
            if not tag_found:
                continue
            try: 
                savePage(link)
            except:
                continue
    
def savePage(url, name = "", location = "SavedPages/"):
    response = urllib.request.urlopen(url)
    webContent = response.read().decode('Windows-1252')
    
    if name == "":
        name = str(url)[str(url).index("="):][1:]

    f = open(location + name + ".html", 'w')
    f.write(webContent)
    f.close

scrapePage("https://geekhack.org/index.php?board=70.0")