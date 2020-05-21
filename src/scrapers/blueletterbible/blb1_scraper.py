"""
Scrape selected authors from blueletterbible.com

from root folder, run:
    python -m src.blueletterbible.blb1_scraper
"""
BLB_catalogue = [
    ("https://www.blueletterbible.org/commentaries/macarthur_john/",
        "MacArthur's Bible Introductions",
        None,
        None),
    ("https://www.blueletterbible.org/commentaries/edersheim_alfred/",
        "The New Schaff-Herzog Encyclopedia of Religious Knowledge",
        1,
        3),
    ("https://www.blueletterbible.org/commentaries/headley_pc/",
        "Women of the Bible",
        1,
        None),
    ("https://www.blueletterbible.org/commentaries/ice_thomas/",
        "History & Authencitity of the Bible / Christology / Attributes of God",
        None,
        None),
    ("https://www.blueletterbible.org/commentaries/ice_thomas/",
        "ASD",
        None,
        None),
    ("https://www.blueletterbible.org/commentaries/lightfoot_jb/",
        "ASD",
        None,
        None)
        
        ]

from collections import Counter 
import datetime
import requests
from bs4 import BeautifulSoup as soup
import json
import json_lines

def commentatorpage_2_links(commentator_link, document_nm_root = '', drop_first=None, drop_last=None):
    """
    Get the links of the commentators work with their respective 
    """
    root_link = commentator_link.split('.org')[0] + '.org'
    r = requests.get(commentator_link)
    r.encoding = r.apparent_encoding
    link = soup(r.text)
    list_of_elements = link.findAll('li',{'class':'articleLI'})
    
    authors = ' '.join([name.capitalize() for name in commentator_link.split('/')[-2].split('_')])
    
    #  get link and document name
    chapter_links = [{
                      'url': root_link+element.a['href'], 
                      'verse_reference':'',
                      'document_nm':document_nm_root+' - '+element.a.text,
                      'authors':authors,
                     }
                     for element in list_of_elements]
    chapter_links = chapter_links[drop_first:]
    if drop_last is not None:
        chapter_links = chapter_links[:-drop_last]
    
    return chapter_links


def remove_footnote_link(string):
    try:
        splitted=string.split('\xa0')
        a=splitted[0]
        b='x'
        if len(splitted)>1:
            b=splitted[1]
        return ''.join([a,b[1:]])
    except:
        print('remove_footnote_link - failed to remove ascii'.upper())
        print(string)
        print(splitted)
        print(a)
        print(b)
        raise
        return string

def chapter_to_list_of_paragraphs( chapter_link ):
    """
    Get list of paragraph strings from chapter page
    
    args:
    ----
        chapter_link: (str) this contains the link to the commentators work
    return:
    ------
        list_of_paragraphs: (list) list of paragraph string
    """
    r = requests.get(chapter_link)
    # https://stackoverflow.com/questions/44203397/python-requests-get-returns-improperly-decoded-text-instead-of-utf-8
    r.encoding = r.apparent_encoding
    link = soup(r.text)
    
    # remove footnotes
    link = soup(str(link.find("div", {"id":"commData"})).split("<hr")[0])
    
    paragraph_elements = link.find("div", {"id":"commData"}).findAll("p")
    list_of_paragraphs = [paragraph_element.text.replace('\n','').strip() 
                          for paragraph_element in paragraph_elements
                          if len(paragraph_element.text.replace('\n','').strip().split(' ') )> 7
                         ]
    
    # remove footnote links 
    list_of_paragraphs = [remove_footnote_link(paragraph)
                          for paragraph in list_of_paragraphs
                         ]
    
    return list_of_paragraphs#, paragraph_elements, link


if __name__=="__main__":
    # BLB_catalogue contains the details
    # of the authors and links scraped from 
    # blue letter bible, manually keys in above
    for commentator_link, document_nm_root, drop_first, drop_last in BLB_catalogue:

        # 1. get chapter links, 
        #    which is a list of dictionaries,
        #    detailing url, verse_ref, document_nm, authors
        chapter_links = commentatorpage_2_links(commentator_link, document_nm_root = '', drop_first=None, drop_last=None)
        print(f"{datetime.datetime.now()} - Scraping commentaries written by {chapter_links['authors']}")

        for commentator_chapter_link in chapter_links:
            
            # 2. for each commentator_chapter_link, 
            #    get a list of paragraphs from chapter
            list_of_paragraphs = chapter_to_list_of_paragraphs( commentator_chapter_link['url'] )

            for paragraph in list_of_paragraphs:

                # 3. save in jsonl format and save to kb

                json_row_to_save = commentator_chapter_link.copy()
                json_row_to_save['paragraph'] = paragraph

                with open("data/blueletterbible.jsonl", 'a') as outfile:
                    json.dump(json_row_to_save, outfile)
                    outfile.write('\n')
            