"""
Scrape the exposition from expositors commentary in 
    url       = "https://biblehub.com/commentaries/expositors/genesis/1.htm"
    last_url  = 'https://biblehub.com/commentaries/expositors/revelation/22.htm'

To save the knowledge bases paragraph by paragraph within a line in a jsonl file
"""

from collections import Counter 
import requests
import datetime
import json
from bs4 import BeautifulSoup as soup

"""
1. Utility functions
"""
def link_to_soup(link):
    """
    Takes in the link and returns the text paragraphs
    """
    import requests
    from bs4 import BeautifulSoup as soup
    r = requests.get(link)
    link = soup(r.text)

    # https://stackoverflow.com/questions/44203397/python-requests-get-returns-improperly-decoded-text-instead-of-utf-8
    r.encoding = r.apparent_encoding

    # get the passages
    soup_ = soup(r.text)
    
    return soup_

def soup_to_paragraphs(url_soup):
    """
    Takes in the soup and retrieves the passage paragraphs
    """
    passages = url_soup.findAll("div", {"class": "chap"})

    text_elements = str(passages).split('<span class="p"><br/><br/></span>')
    paragraphs = [text_element for text_element in text_elements 
                  if (Counter(text_element)['>'] <3) & (Counter(text_element)['>'] <3)]
    
    return paragraphs

def soup_to_next_extension(url_soup):
    """
    The next page would point to an extention, not the full link. e.g. "../genesis/1.htm"
    """
    next_url_extension = url_soup.find("div", {"id": "topheading"}).findAll('a')[-1].get('href')
    next_url_extension = next_url_extension.replace('..','')
    return next_url_extension

def soup_to_verse_references(url_soup):
    """
    Finds the verse references at the top of the page
    (1) the references may overlap, repeats should later be removed
    (2) There may be multiple of them
    
    args:
        url_soup: (bs4.BeautifulSoup) Soup of the page

    Return:
        verse_references: (str) string references of exposited verses 
        e.g. 'Genesis 1:1-31, Genesis 2:1-25'
    """
    passages = url_soup.findAll("div", {"class": "chap"})
    verse_references = passages[0].findAll("span", {"class":"bld"})[0].findAll('a')
    verse_references = ', '.join([verse_reference.text for verse_reference in verse_references])
    
    return verse_references

def save_passage(url, passages, verse_references, authors, save_path='../data/temp.jsonl'):
    """
    Save the knowledge base in a dict line in a jsonl file
    
    args:
        url: (str) link of the referenced paragraph
        passages: (list) list of the string paragraphs
        verse_references: (str) indicates which verse is used here
        authors: (str) credits to the original authors
        save_path: (str) filepath of the jsonl database
        
    Return:
        None
    """
    for paragraph in passages:
        dict_to_save = {'url': url,
                        'paragraph':paragraph,
                        'verse_references':verse_references,
                        'authors':authors
                       }
        with open(save_path, 'a') as outfile:
            json.dump(dict_to_save, outfile)
            outfile.write('\n')


"""
Script logic
"""

# starting and ending url
url = "https://biblehub.com/commentaries/expositors/genesis/1.htm"
last_url = 'https://biblehub.com/commentaries/expositors/revelation/22.htm'

if __name__ == "__main__":

    while True:
        # log 
        print(f"{datetime.datetime.now()} - {url}")

        url_soup = link_to_soup(url)

        # get next URL for the next passage
        next_extension = soup_to_next_extension(url_soup)
        url = '/'.join(url.split('/')[:-2]) + next_extension

        if len(url_soup.findAll("div", {"class": "chap"})[0].findAll("span", {"class":"bld"})) > 0:
            """
            If there is actual content, then:
                1. pull the verse references
                2. pull the passage
                3. save in knowledge base
            else:
                move on

            example of a page without content: 
                https://biblehub.com/commentaries/expositors/genesis/10.htm
            """
            # get verse_references and commentary text
            verse_references = soup_to_verse_references(url_soup)
            passages = soup_to_paragraphs(url_soup)

            # save the verse_references, passages, url
            save_passage(url, passages, verse_references, "Expositors Commentary",
                        save_path='data/expositors_commentary.jsonl')

        # breaking condition: we have reached the last page
        if url==last_url:
            break