from bs4 import BeautifulSoup
from bs4 import Comment

keywords = {"pcb", "case", "oled", }

def load_html(file_path):
    with open("page.html", "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    return soup


def remove_comments(posts):
    for post in posts: #Iterates thru each post (keyword for comments)
        for comment in post.find_all(string=lambda text: isinstance(text, Comment)): #Finds all instances of comment inside of post
            comment.extract() #Removes comment


def format_posts(posts):
    formatted_doc = ""
    for post in posts:
          formatted_post = " ".join(post.get_text().lower().split()) #Removes whitespace
          formatted_doc += formatted_post + "\n\n" #Seperates each post
    return formatted_doc

def find_keywords(doc, keywords):
    #Finds and returns each keyword found in the doc
    found_keywords = []
    for word in keywords:
        if word in doc:
            found_keywords.append(word)
    return found_keywords
