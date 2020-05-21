"""
Basic streamlit app for bibliqal
"""

import streamlit as st
from src.model import USEQA
import numpy as np
import pandas.io.sql as pds
import sqlite3 as sq

# string addresses and questions
vectorised_master_kb_dir = 'data/vectorised_master_sentence_kb.npz'
master_kb_text_dir = 'data/master_kb_sentence_text_clean.db'
saved_model_dir = ''

sample_query_strings = [
    "Did the writer of Genesis intend to convey scientific details of creation?",
    "Was the book of Philemon really written by Apostle Paul or was it forged?",
    "Are the Jews saved by the gospel?",
]



# INIT
@st.cache(allow_output_mutation=True)
def init():
    # init model
    if saved_model_dir == '':
        model = USEQA()

    # init sql connect
    con = sq.connect(master_kb_text_dir, check_same_thread=False)

    # open up numpy array
    with np.load(vectorised_master_kb_dir) as data:
        master_matrix = data['arr_0']

    return model, master_matrix, con

# @st.cache(allow_output_mutation=True)
# def init():
#     # init sql connect
#     # con = sq.connect(master_kb_text_dir, check_same_thread=False)
#     return 1,1,1

model, master_matrix, con = init()



# 1. HEADER AND INTRODUCTION

st.markdown('# bibli<span style="color:orange">qa</span>l', unsafe_allow_html=True)
st.markdown("""
<span style="font-size:1em"> 
bibliqal is an question-answering (QA) engine about the bible.   

It may refer you to articles or commentaries relevant to your clear and verbose questions.
</span>
""", 
unsafe_allow_html=True)


st.sidebar.markdown("""  
__What is the single most important gist of Christianity?__   
bibliqal does not replace actual humans in explaining the faith clearly but
<a href="https://www.youtube.com/watch?v=TXOWyjB7d24">Paul Washer explains it well here.</a>  


__How to contribute.__  
bibliqal needs online resources for non-technical exposition or apologetic texts to grow. Recommend us some. :wink:   
  

__Contact us.__  
ask.bibliqal@gmail.com.  


</br>  
<div style="font-size:0.8em; color:grey">bibliqal is a small non-profit project in continuous development to help people who are curious about the bible to find answers. Servers costs some money and development takes time. Some ads may be displayed to offset the cost.  </div">    

</br>  
""",
unsafe_allow_html=True)





# 2. QUESTION PROCESSING

user_question = st.text_input('Ask your pressing questions here')
if user_question!='':

    # data_df = pds.read_sql('SELECT * FROM master_kb_text WHERE idx IN (1,2,3)', con)
    data_df, top_scores = model.make_query(user_question, master_matrix, con, k=3)

    unique_paragraphs = []
    for idx, row in data_df.iterrows():
        paragraph, sentence = row.paragraph, row.sentence

        if paragraph not in unique_paragraphs:
            unique_paragraphs.append(paragraph)
            surrounding_context = paragraph.split(sentence)

            # color code finder: https://htmlcolorcodes.com/
            markdown_string = surrounding_context[0] + '<span style="background-color: #fccd7a">' + sentence + '</span>' + surrounding_context[1]
            st.markdown(markdown_string, unsafe_allow_html=True)    

            st.markdown('<div style="text-align:right; color:#a1900d">' + row.authors + '</div>', unsafe_allow_html=True)    
            st.markdown(f'<div style="text-align:right; color:#a1900d"> <a href="{row.url}">{row.url}</a> </div>', unsafe_allow_html=True)    
            # st.markdown("<br>", unsafe_allow_html=True)    
            st.markdown("******", unsafe_allow_html=True)  

            # st.dataframe(data_df)
else:
    for sample_query in sample_query_strings:
        st.markdown(f'###### <span style="color: grey"> _{sample_query}_ </span>', unsafe_allow_html=True)    


st.markdown('<head><script data-ad-client="ca-pub-7324103875534556" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script></head>', unsafe_allow_html=True)    

