"""
The raw knowledge base contains imperfections...
... namely, repeats and html text elemnts

Thus, there are two things to do:
    1. Remove repeated paragraphs
    2. Clean the text. Namely font changes
"""

import re
import json
import datetime

def get_verse_ref_from_url(kb_row):
    ref = '-'.join(kb_row['url'].split('.')[-2].split('/')[-2:])
    ref = ref[0].upper() + ref[1:]
    return ref

def remove_text_html_elements(html_paragraph):
    """
    HTML paragraphs has <> elements, 
    for font changes or hyperlinks
    
    This function removes the elements
    
    args:
    ----
        html_paragraph: (str) contains the html elements
    return:
    -------
        result: (str) cleaned paragraph
    """
    result = re.sub("[<].*?[>]", "", html_paragraph)
    result = ' '.join([token for token in result.split(' ') if len(token)>0])
    return result


if __name__=="__main__":
    # read raw
    with open('data/expositors_commentary.jsonl', 'r') as handle:
        kb = handle.read()
    kb = kb.split('\n')
    
    list_of_unique_str = [] # records unique paragraphs
    for kb_row in kb:
        kb_row = json.loads(kb_row)
        
        # remove repeats
        if kb_row['paragraph'] in list_of_unique_str:
            continue
        
        # remove text html elements 
        clean_paragraph = kb_row['paragraph']
        clean_paragraph = remove_text_html_elements(clean_paragraph)
        kb_row['paragraph'] = clean_paragraph

        # add verse references from link
        kb_row['verse_references'] = get_verse_ref_from_url(kb_row)
        
        # save the passage
        with open('data/expositors_commentary_clean.jsonl', 'a') as outfile:
            json.dump(kb_row, outfile)
            outfile.write('\n')


        # trim list_of_unique_str to make it go faster
        list_of_unique_str = list_of_unique_str[:-100:] 
        # log the progress
        print(f"{datetime.datetime.now()} - {kb_row['url']}")