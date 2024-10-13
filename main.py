import webdownloader
import webscrape
import os

def main():
    startUrl = "https://geekhack.org/index.php?board=70.0"

    # Scrapes pages
    totalPages, validLinks = webdownloader.iteratePages(startUrl)
    print(f"Total pages found: {totalPages}")

    # Iterate through saved HTML files in SavedPages
    savedPagesDir = "SavedPages"

    for filename in os.listdir(savedPagesDir):
        if filename.endswith(".html"):  # Making sure only HTML files get searched
            filePath = os.path.join(savedPagesDir, filename)

            soup = webscrape.loadHtml(filePath)
            posts = soup.find_all("div", class_="post")

            webscrape.removeComments(posts)
            doc = webscrape.formatPosts(posts)
            foundKeywords = webscrape.findKeywords(doc, webscrape.keywords)

            if foundKeywords:
                linkName = filename.split(".")[0]  # Removes .html
                correspondingLink = next((link for link in validLinks if linkName in link), None)

                if correspondingLink:
                    print(f"Link with keywords: {correspondingLink}, Keywords Found: {foundKeywords}")

if __name__ == "__main__":
    main()

