import Webdownloader
import webscrape
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
    totalPages, validLinks = Webdownloader.iteratePages()
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

            soup = webscrape.loadHtml(filePath)
            posts = soup.find_all("div", class_="post")

            webscrape.removeComments(posts)
            doc = webscrape.formatPosts(posts)
            foundKeywords = webscrape.findKeywords(doc, st.session_state.keywords)

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