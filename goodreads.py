# Webscraping "API" for Goodreads.com

import requests
from bs4 import BeautifulSoup as bs
import sys


# Cookies needed, push as token:
#   "ubid-main"
#   "x-main"
#   "at-main"


class Goodreads():
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if self.token != None:
            self.session.cookies.update(self.token)
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"}
        )


    def getName(self, id):
        # Gets the displayed name corresponding to id
        url = f"https://www.goodreads.com/user/show/{id}"
        response = self.session.get(url)

        if response.status_code != 200:
            print(f"GET {url} Error {response.status_code}", file=sys.stderr)
            sys.exit(1)

        soup = bs(response.content, "html.parser")

        name = soup.title.string
        name = name.split(" ")

        for i, n in enumerate(name):
            if n[0] == "(":
                name = " ".join(name[0:i])
                break

        return name


    def getShelves(self, id):
        # Returns empty dict if profile is private
        # Returns dict with shelfID = (num of books in shelf, shelfname)

        url = f"https://www.goodreads.com/review/list/{id}"
        response = self.session.get(url)

        if response.status_code != 200:
            print(f"GET {url} Error {response.status_code}", file=sys.stderr)
            sys.exit(1)

        if response.url.find("review") == -1:
            print(f"Profile {id} is private!")
            return []

        soup = bs(response.content, "html.parser")
        
        shelves = {}

        allShelf = soup.find("a", class_="selectedShelf")
        allShelfID = allShelf["href"].split("=")[1]
        
        allShelf = allShelf.string.split(" ")
        allShelfnum = int(allShelf[1].strip("()"))
        allShelfName = allShelf[0]
        shelves[allShelfID] = (allShelfnum, allShelfName)

        for div in soup.find_all("div", class_="userShelf"):
            shelf = div.find("a")
            shelfID = shelf["href"].split("=")[1]
            
            shelf = shelf.string.split("  \u200e")
            num = int(shelf[1].strip("()"))
            shelfName = shelf[0]

            shelves[shelfID] = (num, shelfName)
        return shelves


    def getBooksInShelf(self, id, shelf):
        # Returns the books in a given shelfID for user ID
        # Returns enumerated dict of dicts with book attributes

        titles = []
        authors = []
        asins = []
        isbns = []
        isbn13s = []

        page = 1
        while True:
            print(f"Getting page {page}")
            url = f"https://www.goodreads.com/review/list/{id}?shelf={shelf}&page={page}"
            response = self.session.get(url)
            page += 1

            if response.status_code != 200:
                print(f"GET {url} Error {response.status_code}", file=sys.stderr)
                sys.exit(1)

            if response.url.find("review") == -1:
                print(f"Profile {id} is private!")
                return {}

            if response.text.find("No matching items!") != -1:
                break

            soup = bs(response.content, "html.parser")

            _titles = soup.find_all('td', class_='title')
            _authors = soup.find_all('td', class_='author')
            _asin = soup.find_all('td', class_='asin')
            _isbn = soup.find_all('td', class_='isbn')
            _isbn13 = soup.find_all('td', class_='isbn13')


            #TODO These are quite similar in how they're accessed, rewrite to get different attributes based on supplied parameter/args?
            # Ex: gr.getBooksInShelf(id, shelf, attr = {"title", "author", "isbn", etc})

            # cover
            # title
            # author
            # isbn
            # isbn13
            # asin
            # num_pages
            # avg_rating
            # num_ratings
            # date_pub
            # date_pup_edition
            # rating
            # shelves
            # review
            # notes
            # comments
            # votes
            # read_count
            # date_started
            # date_read
            # date_added
            # owned
            # format


            # <td class="field title"><label>title</label>
            #  <div class="value"> <a href="/book/show/22886612-nemesis-games" title="Nemesis Games (The Expanse, #5)">
            #      Nemesis Games
            #      <span class="darkGreyText">(The Expanse, #5)</span>
            #    </a></div>
            # </td>

            for t in _titles:
                _t = t.find("a")
                title = _t["title"].strip()
                titleID = _t["href"].split("/book/show/")[1]
                titles.append((title, titleID))

           
            for a in _authors:
                _a = a.find("a")
                author = _a.string.strip()
                authorID = _a["href"].split("/author/show/")[1]
                authors.append((author, authorID))

            for a in _asin:
                _a = a.find("div", class_="value")
                asin = _a.string.strip()
                asins.append(asin)


            for i in _isbn:
                _i = i.find("div", class_="value")
                isbn = _i.string.strip()
                isbns.append(isbn)


            for i in _isbn13:
                _i = i.find("div", class_="value")
                isbn13 = _i.string.strip()
                isbn13s.append(isbn13)

        books = {}
        for id, (asin, isbn, isbn13, (title, titleID), (author, authorID)) in enumerate(zip(asins, isbns, isbn13s, titles, authors)):
           books[id] = {
            "title": title,
            "titleID": titleID,
            "author": author,
            "authorID": authorID,
            "asin": asin,
            "isbn": isbn,
            "isbn13": isbn13
           }

        return books