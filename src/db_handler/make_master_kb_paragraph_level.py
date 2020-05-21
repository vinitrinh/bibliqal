"""
Make a master frame of:
    1. Knowledge base in text
    2. Vectorised knowledge base

To run:
    python -m src.make_master_kb
"""
import os
import datetime
from pprint import pprint

import numpy as np
import sqlite3 as sq
import json_lines

from ..model import USEQA


"""
List of KB files to iterate through and save into kb 
"""
jsonl_kbs_to_process = [
    'data/expositors_commentary_clean.jsonl', 
    'data/blueletterbible.jsonl',
    ]
master_kb_text_dir = 'data/master_kb_text.db'
vectorised_master_kb_dir = 'data/vectorised_master_kb.npz'


"""
filter_jsonl contains the filtering for 
rows that we do not want.

Remove if:
    1. number of whitespace tokens is less than 50
"""
def filter_jsonl(jsonl):
    """
    Returns True if this is the kind of jsonl 
    that we want in our master kb
    """
    if len(jsonl['paragraph'].split()) < 50:
        return False
    return True


if __name__=="__main__":
    """
    init the model

    for every knowledge base, 
        for every line in each knowledge base,
            Check if line fits requirements
                encode sentence and save the paragraph
    """

    # init model
    model = USEQA()
    
    # init db -> this means creating it from scratch
    if os.path.exists(master_kb_text_dir):
        os.remove(master_kb_text_dir)
    con = sq.connect(master_kb_text_dir)
    query = 'CREATE TABLE master_kb_text (idx real, authors text, document_nm text, paragraph text, url text, verse_references text)'
    con.execute(query)
    con.commit() 

    # start process loop
    vectorised_master_kb = []
    k, idx = 0, 0
    for jsonl_kbs in jsonl_kbs_to_process:

        with open(jsonl_kbs, 'rb') as jsonl_kb_file:
            for json_line in json_lines.reader(jsonl_kb_file):
                
                # log
                k+=1
                if k%10==0:
                    print(f"{datetime.datetime.now()} - {k}")

                if filter_jsonl(json_line):
                    # if True: 
                    #       (1) encode the context and save numpy array
                    #       (2) save the paragraph in sqllite
                    # print("\n"+json_line['paragraph']+"\n")

                    # 1. encode context
                    vectorised_master_kb.append( 
                        model.predict(json_line['paragraph'],type='response').numpy() 
                        )

                    # 2. save sqlite
                    rowinfo = [idx] + [json_line.get(key,'') for key in ['authors', 'document_nm', 'paragraph', 'url', 'verse_references']]
                    con.execute('INSERT INTO master_kb_text VALUES (?, ?, ?, ?, ?, ?)', rowinfo)
                    # con.commit()

                    # update index
                    idx+=1
                else:
                    pass

    # save changes and close
    con.commit()
    con.close()
    # save the vectorized db
    vectorised_master_kb = np.vstack(vectorised_master_kb)
    np.savez(vectorised_master_kb_dir, vectorised_master_kb)


