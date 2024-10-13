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
