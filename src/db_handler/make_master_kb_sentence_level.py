"""
Make a master frame of:
    1. Knowledge base in text
    2. Vectorised knowledge base

Currently, there are repeats. Cant we remove them somehow easily with pandas?

Perhaps we can save it with pandas:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html

To run:
    python -m src.make_master_kb_sentence_level
"""
import os
import datetime
from pprint import pprint

import pandas.io.sql as pds
import numpy as np
import sqlite3 as sq
import json_lines
import spacy

from ..model import USEQA



"""
List of KB files to iterate through and save into kb 
"""
jsonl_kbs_to_process = [
    'data/expositors_commentary_clean.jsonl', 
    'data/blueletterbible.jsonl',
    ]

master_kb_text_dir = 'data/master_kb_sentence_text.db'
master_kb_text_clean_dir = 'data/master_kb_sentence_text_clean.db'

vectorised_master_kb_dir = 'data/vectorised_master_sentence_kb.npz'







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
    if (len(jsonl['paragraph'].split()) < 50):
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

    # init model and spacy model to split sentences
    
    nlp = spacy.load('en')

    def sentence_tokenize(paragraph):
        """
        Split a paragraph string into a list of string sentences

        https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
        """
        tokens = nlp(paragraph)
        return [str(sent.string.strip()) for sent in tokens.sents]





    """
    1. READ THE INDIVIDUAL KNOWLEDGE BASES AND SAVE TO SQL
    """
    # init db -> this means creating it from scratch
    if os.path.exists(master_kb_text_dir):
        os.remove(master_kb_text_dir)
    con = sq.connect(master_kb_text_dir)
    query = 'CREATE TABLE master_kb_text (idx real, sentence text, paragraph text, authors text, document_nm text, url text, verse_references text)'
    con.execute(query)
    con.commit() 

    # start process loop
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
                    
                    for sentence in sentence_tokenize(json_line['paragraph']):
                        
                        if len(sentence) > 4:
                            pass

                        # 1. save sqlite
                        rowinfo = [idx] + [sentence] + [json_line.get(key,'') for key in ['paragraph', 'authors', 'document_nm', 'url', 'verse_references']]
                        con.execute('INSERT INTO master_kb_text VALUES (?, ?, ?, ?, ?, ?, ?)', rowinfo)
                        
                        if idx%100==0:
                            con.commit()

                        # update index
                        idx+=1
                else:
                    pass

    # save changes and close
    con.commit()
    print("unclean kb saved")
    del nlp





    """
    2. REMOVE THE DUPLICATES AND APPLY CLEANING HERE
       PULL TABLE AND SET INDEX
    """
    data_df = pds.read_sql('SELECT * FROM master_kb_text', con)
    data_df = data_df.set_index('idx')
    con.close()

    # CLEANING THE SENTENCES
    # dropping duplicates
    print(f"{len(data_df)} before")
    data_df = data_df.drop_duplicates('sentence')
    print(f"{len(data_df)} after")
    # Remove small sentences that are made of 4 characters or less
    # data_df = data_df[data_df.sentence.apply(len) > 4]

    # set index
    data_df = data_df.assign(idx = np.arange(len(data_df)))
    data_df = data_df.set_index('idx')

    # save the clean text kb into a new sql base
    if os.path.exists(master_kb_text_clean_dir):
        os.remove(master_kb_text_clean_dir)
    con = sq.connect(master_kb_text_clean_dir)
    query = 'CREATE TABLE master_kb_text (idx real, sentence text, paragraph text, authors text, document_nm text, url text, verse_references text)'
    con.execute(query)
    data_df.to_sql('master_kb_text', con=con, if_exists='replace')
    con.close()







    """
    3. sAVE MASTER VECTORIZED KNOWLEDGE BASE
    """
    model = USEQA()

    def encode_sentence_paragraph(i, sentence, paragraph):
        if i%10==0:
            print(f"{datetime.datetime.now()} - {i}")
        return model.predict(sentence, context = paragraph ,type='response').numpy() 

    # Here we save the vectorised 
    vectorised_master_kb = [encode_sentence_paragraph(i, row.sentence, row.paragraph) for i, row in data_df.iterrows()]

    # save the vectorized db
    vectorised_master_kb = np.vstack(vectorised_master_kb)
    np.savez(vectorised_master_kb_dir, vectorised_master_kb)
    print("Master vector saved")
