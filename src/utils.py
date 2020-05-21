import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def find_pos_of_nth_smallest(sortargs, n):
    """
    Find the position of the nth smallest number
    
    args:
        sortargs: (list) contains the rankings
        n: (int) number positions of smallest number
        
    return:
        integer postion of the value
    """
    return sortargs.index(sorted(sortargs)[n])

def find_idx_of_best_k_answers(sortargs, k):
    """
    Find indices of the most relevant 
    
    args:
        sortargs: (list) contains the rankings
        k: (int) number positions of top rankings
        
    return:
        list of top k ranking positions in lists
        
    e.g.
    >>> find_idx_of_best_k_answers(sortargs, 5)
    >>> [3, 4, 2, 43, 5]
    
    where 3 is the index of 0, 
          4 is the index of 1,
          2 is the index of 2,
          43 is the index of 3,
          5 is the index of 4
    """
    return [find_pos_of_nth_smallest(sortargs, i) for i in range(k)]

def query_SQL_by_idx(con, idx):
    """
    Query an observation from SQL base based on idx
    
    args:
    -----
        con: SQL client
        idx: (int) index position of the row in the database
        
    return:
    ------
        query_results: list of tuple
    """
    return con.execute('SELECT * FROM master_kb_text WHERE idx = ?', (idx,)).fetchall() 




def question_cleaner(df_query):
    kb=([int(xx) for xx in (df_query[3].iloc[0]).split(' ')])
    gt = [int(xx) for xx in (df_query[2].iloc[0]).split(' ')]
    ct=0
    negg=0
    withans=[]
    for ii in range(len(df_query)):
        kb=[int(xx) for xx in (df_query[3].iloc[ii]).split(' ')]
        gt = [int(xx) for xx in (df_query[2].iloc[ii]).split(' ')]
        if bool(set(gt) & set(kb)):
            withans.append(ii)
        else:
            negg+=1
    print('total:{}, removed:{}, remainder:{}'.format(len(df_query), negg, len(withans)))
    return df_query.iloc[withans]


def clean_txt(text):
    """Strips formatting"""
    text=[x.replace('\n', '. ') for x in text] # not sure how newlines are tokenized
    text=[x.replace('.. ', '. ').rstrip() for x in text] # remove artifact
    return text


def ranker(model, question_vectors, df_query, df_doc):
    """for model evaluation on InsuranceQA datset"""
    predictions=[]
    gts=[]
    for ii, question_vector in enumerate(question_vectors):
        kb=[int(xx) for xx in (df_query[3].iloc[ii]).split(' ')]
        gt = [int(xx) for xx in (df_query[2].iloc[ii]).split(' ')]
        doc_vectors = model.predict(df_doc.loc[kb]['text'].tolist())
        cossim = cosine_similarity(doc_vectors, question_vector.reshape(1, -1))
        sortargs=np.flip(cossim.argsort(axis=0))
        returnedans = [kb[jj[0]] for jj in sortargs]
        predictions.append(returnedans)
        gts.append(gt)
    return predictions, gts
        
def scorer(predictions, gts, k=3):
    """For model evaluation on InsuranceQA datset. Returns score@k."""
    score=0
    total=0
    for gt, prediction in zip(gts, predictions):
        if bool(set(gt) & set(prediction[:k])):
            score+=1
        total+=1
    return score/total

def make_pred(row, gr, query_col_name='queries', top_k=3):
    """Make line by line predictions, returns top 3 index of kb."""
    txt, ind = gr.make_query(row['queries'], top_k=top_k, index=True)
    return ind

def make_iscorr(row, prediction_col_name='predictions', answer_col_name='answer'):
    """Calculates accuracy @3."""
    if bool(set(row[answer_col_name]) & set(row[prediction_col_name])):
        return 1
    else: return 0
    
def make_closewrong(row, prediction_col_name='predictions', answer_col_name='answer'):
    """Find index of wrong answer with highest similarity score aka hardmining."""
    try: return [x for x in row[prediction_col_name] if x not in row[answer_col_name]][0]
    except: return 1 #Just return the most common class as the negative eg.
    