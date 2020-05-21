"""
This script tests that the whole system works

to run from root folder:
    python -m src.test
"""

import numpy as np
import sqlite3 as sq
from .model import USEQA

if __name__=="__main__":
    
    # string addresses and questions
    vectorised_master_kb_dir = 'data/vectorised_master_sentence_kb.npz'
    master_kb_text_dir = 'data/master_kb_sentence_text_clean.db'
    query_strings = [
        "Is Genesis a scientific document?",
        "Was the book of Philemon really written by Apostle Paul or was it forged?",
        "Are the Jews saved by the gospel?",
    ]

    # load master kb
    with np.load(vectorised_master_kb_dir) as data:
        master_matrix = data['arr_0']

    # sql connection
    con = sq.connect(master_kb_text_dir)

    # init model
    model = USEQA()
    k=1
    for query_string in query_strings:
        data_df, top_scores = model.make_query(query_string, master_matrix, con)
        k+=1

        print("")
        print(f"Question {k}: {query_string}")
        print("")
        for i, row in data_df.iterrows():
            print(f"Answer {i}: {row.paragraph}")
            print("")



