##Webdownloader.py
import urllib.request, urllib.error, urllib.parse
import streamlit as st
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
    validLinks = []

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
                validLinks.append(link)
            except:
                continue
    nextPage = None
    #find our next link (technically we could do this all in one loop but then it gets ugly)
    for posNextLink in indexPage.find_all("a"):
        htmlClass = posNextLink.get('class')
        htmlContents = posNextLink.contents
        if(htmlClass and htmlClass[0] == "navPages" and htmlContents and htmlContents[0] == "»"):
            nextPage = posNextLink.get('href')
            break
    return validLinks, nextPage
    
def savePage(url, name = "", location = "SavedPages/"):
    response = urllib.request.urlopen(url)
    webContent = response.read().decode('Windows-1252')
    
    if name == "":
        name = str(url)[str(url).index("="):][1:]

    f = open(location + name + ".html", 'w')
    f.write(webContent)
    f.close()

def iteratePages():
    nextPage = "https://geekhack.org/index.php?board=70"
    page = 0
    links = []

    while nextPage and (page < st.session_state.page_limit if isinstance(st.session_state.page_limit, int) else True):
        page += 1
        print(f"Scraping Page: {page}. Url: {nextPage}")
        st.session_state.messages.append(f"Scraping Page: {page}. Url: {nextPage}")

        validLinks, nextPage = scrapePage(nextPage)
        
        links.extend(validLinks)
    
    return page, links

##webscrape.py
from bs4 import BeautifulSoup
from bs4 import Comment

keywords = {"pcb", "case", "oled", }

def loadHtml(filePath):
    with open(filePath, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup

def removeComments(posts):
    for post in posts: #Iterates thru each post (keyword for comments)
        for comment in post.find_all(string=lambda text: isinstance(text, Comment)): #Finds all instances of comment inside of post
            comment.extract() #Removes comment

def formatPosts(posts):
    formattedDoc = ""
    for post in posts:
          formattedPost = " ".join(post.get_text().lower().split()) #Removes whitespace
          formattedDoc += formattedPost + "\n\n" #Seperates each post
    return formattedDoc

def findKeywords(doc, keywords):
    #Finds and returns each keyword found in the doc
    foundKeywords = []
    for word in keywords:
        if word in doc:
            foundKeywords.append(word)
    return foundKeywords

##main
import os 
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import threading  #multithreading
import json  # Saving links file
from time import sleep
from queue import Queue
from pathlib import Path
from shutil import rmtree

VALID_LINKS_FILE = "SavedPages/valid_links.json"

if "link_results" not in st.session_state:
    st.session_state.link_results = []
if "keyword_input" not in st.session_state:
    st.session_state.keyword_input = "Enter keywords separated by commas"
if "scrape_running" not in st.session_state:
    st.session_state.scrape_running = False
if "parse_running" not in st.session_state:
    st.session_state.parse_running = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "keywords" not in st.session_state:
    st.session_state.keywords = []
if "page_limit" not in st.session_state:
    st.session_state.page_limit = None

def scrapePages():
    # Scrapes pages
    totalPages, validLinks = iteratePages()
    print(f"Total pages found: {totalPages}")
    updateStatus(f"Total pages found: {totalPages}")
    saveLinks(validLinks)
    return validLinks

def parsePages(validLinks):
    # Iterate through saved HTML files in SavedPages
    savedPagesDir = "SavedPages"

    for filename in os.listdir(savedPagesDir):
        if filename.endswith(".html"):  # Making sure only HTML files get searched
            filePath = os.path.join(savedPagesDir, filename)
            print(f"Parsing Page: {filePath}")
            updateStatus(f"Parsing Page: {filePath}")

            soup = loadHtml(filePath)
            posts = soup.find_all("div", class_="post")

            removeComments(posts)
            doc = formatPosts(posts)
            foundKeywords = findKeywords(doc, st.session_state.keywords)

            if foundKeywords:
                linkName = filename.split(".")[0]  # Removes .html
                correspondingLink = next((link for link in validLinks if linkName in link), None)

                if correspondingLink:
                    st.session_state.link_results.append(f"{correspondingLink}\nKeywords Found: {foundKeywords}")

def saveLinks(links):
    ourPath = Path(VALID_LINKS_FILE)
    ourPath.parent.mkdir(parents=True, exist_ok=True)
    with open(ourPath, "w") as f:  # Creates file if doesn't exist
        json.dump(links, f)

def loadLinks():
    if os.path.exists(VALID_LINKS_FILE):
        with open(VALID_LINKS_FILE, "r") as f:
            data = json.load(f)
            return data if data else []  # Return empty list if the file contains []
    else:
        saveLinks([])  # Creates file w/empty list if it doesnt exist
        return []

if "valid_links" not in st.session_state:
    st.session_state.valid_links = loadLinks()

def deleteExistingFiles():
    ourPath = Path(VALID_LINKS_FILE)
    ourPath.parent.mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(ourPath.parent):
        if filename.endswith(".html"):  # Only delete HTML files
            filePath = os.path.join(ourPath.parent, filename)
            os.remove(filePath)  # Delete the file

def updateStatus(message):
    st.session_state.messages.append(message)

def onScrapeButton():
    updateStatus("Scraping in progress...")
    if not st.session_state.valid_links:
        deleteExistingFiles()
        st.session_state.valid_links = scrapePages()
        updateStatus("Scraping completed")
        updateStatus("DONE")
    else:
        updateStatus("Valid links already exist. Skipping scraping.")
        updateStatus("DONE")
    st.session_state.scrape_running = False

def onParseButton():
    updateStatus("Parsing in progress...")
    if not st.session_state.valid_links:
        updateStatus("You need to scrape first to get valid links.")
        updateStatus("ERROR")
    else:
        st.session_state.link_results.clear()
        parsePages(st.session_state.valid_links)
        updateStatus("Parsing Complete.")
        updateStatus("DONE")
    st.session_state.parse_running = False

def onUpdateKeywords():
    keyword_input = st.session_state.keyword_input
    st.session_state.keywords = [keyword.strip() for keyword in keyword_input.split(",")]
    st.write("Keywords updated.")

def wipeCache():
    rmtree(Path(VALID_LINKS_FILE).parent)
    st.session_state.valid_links = []

# Thread wrappers
def scrapeThread():
    st.session_state.scrape_running = True
    st.session_state.messages = []
    t = threading.Thread(target=onScrapeButton)
    add_script_run_ctx(t, get_script_run_ctx())
    t.start()

def parseThread():
    st.session_state.parse_running = True
    st.session_state.messages = []
    t = threading.Thread(target=onParseButton)
    add_script_run_ctx(t, get_script_run_ctx())
    t.start()

st.title("GeekHack Webscraper")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button("Scrape",disabled=st.session_state.scrape_running or st.session_state.parse_running,on_click=scrapeThread, help="This button will scrape up to the number of pages indicated in the Page Limit box for valid posts regarding currently avalible keyboards. This can be a time intensive process.")
with col2:
    st.button("Parse",disabled=st.session_state.scrape_running or st.session_state.parse_running,on_click=parseThread, help="This button will parse the valid posts and only return the links to those which contain the provided keywords.")
with col3:
    st.number_input("Page Limit", value=None,key="page_limit",help="Limits the maximium number of pages to scrape off of GeekHack. Leave blank to set to unlimited.",format="%d",step=1)
with col4:
    st.button("Wipe Saved Pages",disabled=st.session_state.scrape_running or st.session_state.parse_running or not st.session_state.valid_links,on_click=wipeCache,help="Deletes the scraped pages off the cache.",type="primary")

# Keyword input
st.text_input("Keywords", key="keyword_input", on_change=onUpdateKeywords)

with st.status("Waiting" if not (st.session_state.scrape_running or st.session_state.parse_running) else "Scraping..." if st.session_state.scrape_running else "Parsing...", expanded=st.session_state.scrape_running or st.session_state.parse_running, state="running") as statusB:
    for message in st.session_state.messages:
        if message == "DONE": statusB.update(label="Complete", state="complete", expanded=False)
        elif message == "ERROR": statusB.update(label="Error", state="error")
        else: st.write(message)

# Display links found
if st.session_state.link_results:
    with st.expander("Found Links"):
        for link in st.session_state.link_results:
            st.markdown(f"[{str(link).split("\n")[0]}]({str(link).split("\n")[0]})\n{str(link).split("\n")[1]}")

if st.session_state.scrape_running or st.session_state.parse_running:
    sleep(0.5)
    st.rerun()