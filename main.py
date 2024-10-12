import webdownloader
import webscrape
import os

def main():
    start_url = "https://geekhack.org/index.php?board=70.0"
    
    total_pages = webdownloader.iteratePages(start_url)
    print(f"Total pages found: {total_pages}")

    soup = webscrape.load_html("SavedPages/index.html")
    posts = soup.find_all("div", class_="post") #Scraps each post class
    saved_pages_dir = "SavedPages"

   
    for filename in os.listdir(saved_pages_dir):
        file_path = os.path.join(saved_pages_dir, filename)
        #print(f"Processing file: {file_path}")

        soup = webscrape.load_html(file_path)
        posts = soup.find_all("div", class_="post")
         
        webscrape.remove_comments(posts)
        doc = webscrape.format_posts(posts)
        found_keywords = webscrape.find_keywords(doc, webscrape.keywords)

        formatted_doc = " ".join(doc.split())

        print(f"Formatted Text:\n{formatted_doc}\n\nKeywords Found: {found_keywords}")
