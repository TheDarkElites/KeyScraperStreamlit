import Webdownloader
import webscrape
import os 
import tkinter as tk  # GUI
import threading  # GUI still usable during long tasks
import json  # Saving links file

VALID_LINKS_FILE = "SavedPages/valid_links.json"
validLinks = []
keywords = []  # Store keywords globally

def scrapePages():
    startUrl = "https://geekhack.org/index.php?board=70.0"

    # Scrapes pages
    totalPages, validLinks = Webdownloader.iteratePages(startUrl)
    print(f"Total pages found: {totalPages}")
    saveLinks(validLinks)
    return validLinks

def parsePages(validLinks):
    # Iterate through saved HTML files in SavedPages
    savedPagesDir = "SavedPages"

    for filename in os.listdir(savedPagesDir):
        if filename.endswith(".html"):  # Making sure only HTML files get searched
            filePath = os.path.join(savedPagesDir, filename)

            soup = webscrape.loadHtml(filePath)
            posts = soup.find_all("div", class_="post")

            webscrape.removeComments(posts)
            doc = webscrape.formatPosts(posts)
            foundKeywords = webscrape.findKeywords(doc, keywords)

            if foundKeywords:
                linkName = filename.split(".")[0]  # Removes .html
                correspondingLink = next((link for link in validLinks if linkName in link), None)

                if correspondingLink:
                    # Update link display on the main thread
                    root.after(0, updateLinkDisplay, f"{correspondingLink}\nKeywords Found: {foundKeywords}")

def saveLinks(links):
    with open(VALID_LINKS_FILE, "w") as f:  # Creates file if doesn't exist
        json.dump(links, f)

def loadLinks():
    if os.path.exists(VALID_LINKS_FILE):
        with open(VALID_LINKS_FILE, "r") as f:
            data = json.load(f)
            return data if data else []  # Return empty list if the file contains []
    else:
        saveLinks([])  # Creates file w/empty list if it doesnt exist
        return []

def deleteExistingFiles():
    savedPagesDir = "SavedPages"
    for filename in os.listdir(savedPagesDir):
        if filename.endswith(".html"):  # Only delete HTML files
            filePath = os.path.join(savedPagesDir, filename)
            os.remove(filePath)  # Delete the file

def onScrapeButton():
    # Check if the valid_links.json file is empty or doesn't exist
    global validLinks
    if not validLinks or validLinks == []:
        deleteExistingFiles()
        updateStatus("Scraping in progress...")
        disableButtons()
        validLinks = scrapePages()
        updateStatus("Scraping completed.")
    else:
        updateStatus("Valid links already exist. Skipping scraping.")
    
    enableButtons()

def onParseButton():
    global validLinks
    if not validLinks:  # Check if scrape has already been done
        updateStatus("You need to scrape first to get valid links.")
    else:
        updateStatus("Parsing in progress...")
        disableButtons()
        clearLinks()
        parsePages(validLinks)
        updateStatus("Parsing completed.")
        enableButtons()

def onUpdateKeywords():
    global keywords
    # Get the keywords from the input box, split by commas, and strip whitespace
    keyword_input = keywordsEntry.get()
    keywords = [keyword.strip() for keyword in keyword_input.split(",")]
    updateStatus("Keywords updated.")

def scrapeThread():  # Scrapes in background so GUI doesnt crash
    threading.Thread(target=onScrapeButton).start()

def parseThread():  # Parses in background so GUI doesnt crash
    threading.Thread(target=onParseButton).start()

def enableButtons():  # Enables buttons after process
    scrapeBtn.config(state=tk.NORMAL)
    parseBtn.config(state=tk.NORMAL)

def disableButtons():  # Disables buttons during process
    scrapeBtn.config(state=tk.DISABLED)
    parseBtn.config(state=tk.DISABLED)

def updateStatus(message):  # Updates status message
    statusLabel.config(text=message)

def clearLinks():  # Clears links before parsing
    linksTextBox.config(state=tk.NORMAL)
    linksTextBox.delete(1.0, tk.END)  # Clear the text box
    linksTextBox.config(state=tk.DISABLED)

def updateLinkDisplay(linkInfo):  # Adds links to display
    linksTextBox.config(state=tk.NORMAL)  # Enables editing
    linksTextBox.insert(tk.END, linkInfo + "\n")
    linksTextBox.config(state=tk.DISABLED)  # Disables editing

root = tk.Tk()
root.title("GeekHack Webscraper")

scrapeBtn = tk.Button(root, text="Scrape", command=scrapeThread)
parseBtn = tk.Button(root, text="Parse", command=parseThread)
scrapeBtn.grid(row=0, column=0, padx=10, pady=10)
parseBtn.grid(row=0, column=1, padx=10, pady=10)

statusLabel = tk.Label(root, text="Ready")
statusLabel.grid(row=1, column=0, columnspan=2, pady=10)

# Set the width of the text box to 90
linksTextBox = tk.Text(root, height=15, width=90, state=tk.DISABLED)  # Wider text box
linksTextBox.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

scrollbar = tk.Scrollbar(root, command=linksTextBox.yview)
linksTextBox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=2, column=2, sticky="ns")

# Create an entry box for keywords
keywordsEntry = tk.Entry(root, width=50)
keywordsEntry.grid(row=3, column=0, padx=10, pady=10)

# Place the update keywords button next to the keywords entry
updateKeywordsBtn = tk.Button(root, text="Update Keywords", command=onUpdateKeywords)
updateKeywordsBtn.grid(row=3, column=1, padx=10, pady=10)

keywordsEntry.insert(0, "Enter keywords separated by commas")  # Placeholder text

validLinks = loadLinks()
root.mainloop()