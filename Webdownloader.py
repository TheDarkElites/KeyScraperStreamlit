import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

whitelistTags = ["[gb]", "instock"]
blacklistTags = ["closed", "completed", "complete", "cancelled"]

def scrapePage(url):
    #loads up index page of forums to scrape through
    savePage(url, "index", "")
    f = open("index.html", "r")

    #Creates soup
    indexPage = BeautifulSoup(f, "html.parser")

    validPost = False

    #Finds all td divs and iterates through
    for post in indexPage.find_all("td"):
        #throw out any results that dont contain the post link
        if post.get('class')[0] != "subject" or post.get('class')[1] != "windowbg2":
            continue

        #Go through a divs (for link)
        for postA in post.find_all("a"):
            #gets the actual link to the keyboard post
            link = postA.get("href")

            #filter out links that arent to the actual post (profile links)
            if str(link).find("profile") != -1:
                continue

            #get the link text
            text = postA.contents[0]
            text = text.lower()

            #throw out links that contain blacklisted terms
            for tag in blacklistTags:
                if text.find(tag) != -1:
                    continue

            #throw out links that contain no whitelisted terms
            tag_found = False
            for tag in whitelistTags:
                if text.find(tag) != -1:
                    tag_found = True
            if not tag_found:
                continue

            #save page using savePage
            try: 
                savePage(link)
                validPost = True
            except:
                continue
    return validPost
    
def savePage(url, name = "", location = "SavedPages/"):
    response = urllib.request.urlopen(url)
    webContent = response.read().decode('Windows-1252')
    
    if name == "":
        name = str(url)[str(url).index("="):][1:]

    f = open(location + name + ".html", 'w')
    f.write(webContent)
    f.close

def iteratePages(start_url):
    url = start_url
    page = 0

    while True:
        page+=1
        print(f"Scraping Page: {page}. Url: {url}")

        if not scrapePage(url): #Tries to scrape the URL. Will fail when out of pages
            break

        url = f"https://geekhack.org/index.php?board=70.{page*50}" #Each URL goes up in increments of 50
        #ERROR: Breaks on page 46
    
    return page
