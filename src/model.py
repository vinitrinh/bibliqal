"""
Model script contains utiity function for model class
Model class contains, QA model, inference functions
"""
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.optimizers import Adam
import pandas.io.sql as pds
import numpy as np
import datetime

from .utils import *
from .metric_learning import triplet_loss


# tf.config.set_visible_devices(tf.config.list_physical_devices()[0])

class USEQA:
    
    def __init__(self):
        self.v=['QA/Final/Response_tuning/ResidualHidden_1/dense/kernel','QA/Final/Response_tuning/ResidualHidden_0/dense/kernel', 'QA/Final/Response_tuning/ResidualHidden_1/AdjustDepth/projection/kernel']
        self.questions = {}

        # init saved model
        self.embed = hub.load('https://tfhub.dev/google/universal-sentence-encoder-qa/3')
        self.init_signatures()


    def init_signatures(self):
        # re-initialize the references to the model signatures
        self.question_encoder = self.embed.signatures['question_encoder']
        self.response_encoder = self.embed.signatures['response_encoder']
        self.neg_response_encoder = self.embed.signatures['response_encoder']
        print('model initiated!')

        # optimizer
        self.optimizer = tf.keras.optimizers.Adam()
        self.cost_history = []
        self.var_finetune=[x for x in self.embed.variables for vv in self.v if vv in x.name] #get the weights we want to finetune.
        
        
    def predict(self, text, context=None, type='response'):
        """Return the tensor representing embedding of input text.
        Type can be 'query' or 'response' """
        if type=='query':
            if isinstance(text, str):
                return self.question_encoder(tf.constant([text]))['outputs']
            elif hasattr(text, '__iter__'):
                return self.question_encoder(tf.constant(text))['outputs']
            
        elif type=='response':
            if isinstance(text, str):
                text = [text]
                if not context:
                    context = text
                else:
                    context = [context]
            try:
                if not context:
                    context = text
                return self.response_encoder(input=tf.constant(text),
                                            context=tf.constant(context))['outputs']
            except:
                encoded_text=[]
                for one_text in text:
                    one_text = ' '.join(one_text.split(' ')[:100])
                    if not context:
                        context = one_text
                    encoded_text.append(self.response_encoder(input=tf.constant(one_text),
                                        context=tf.constant(context))['outputs'])
                    return tf.concat(encoded_text, axis=0)

        else: print('Type of prediction not defined')
        
    def make_query(self, querystring, vectorized_knowledge, con, k=5, predict_type='query'):
        """Make a query against the stored vectorized knowledge. 
        Choose index=True to return sorted index of matches.
        type can be 'query' or 'response' if you are comparing statements
        """
        # score the stuff
        similarity_score=cosine_similarity(vectorized_knowledge, self.predict([querystring], type=predict_type))
        idx_of_best_k_answers = np.flip(np.argsort(similarity_score.flatten().tolist())[-k:])
        # in decreasing order of relevance

        top_k_scores = similarity_score[idx_of_best_k_answers]

        # call from sql
        data_df = pds.read_sql('SELECT * FROM master_kb_text WHERE idx IN (' + str(list(idx_of_best_k_answers))[1:-1] + ')', con)
        data_df = data_df.set_index('idx').loc[idx_of_best_k_answers]
        return data_df, top_k_scores
        
        
    def finetune(self, question, answer, context, margin=0.3, loss='triplet', neg_answer=[], neg_answer_context=[], label=[]):

        with tf.GradientTape() as tape:
            # get encodings
            question_embeddings = self.question_encoder(tf.constant(question))['outputs']
            response_embeddings = self.response_encoder(input=tf.constant(answer), 
                                                        context=tf.constant(context))['outputs']

            if loss == 'cosine':
                """
                # https://www.tensorflow.org/api_docs/python/tf/keras/losses/CosineSimilarity
                """
                self.cost = tf.keras.losses.CosineSimilarity(axis=1)
                cost_value = self.cost(question_embeddings, response_embeddings)
                
            elif loss == 'triplet':
                """
                Triplet loss uses a non-official self-implementated loss function outside of TF based on cosine distance
                """
                neg_response_embeddings = self.neg_response_encoder(input=tf.constant(neg_answer), 
                                                                    context=tf.constant(neg_answer_context))['outputs']
                cost_value = triplet_loss(question_embeddings, response_embeddings, neg_response_embeddings)

                
        # record loss     
        self.cost_history.append(cost_value.numpy().mean())
        
        # apply gradient
        grads = tape.gradient(cost_value, self.var_finetune)
        self.optimizer.apply_gradients(zip(grads, self.var_finetune))

        return cost_value.numpy().mean()
        
    def export(self, savepath='fine_tuned'):
        '''
        Path should include partial filename.
        https://www.tensorflow.org/api_docs/python/tf/saved_model/save
        '''
        tf.saved_model.save(self.embed, savepath, signatures={
                                                                'default': self.embed.signatures['default'],
                                                                'response_encoder':self.embed.signatures['response_encoder'],
                                                                'question_encoder':self.embed.signatures['question_encoder']  
                                                                })

    def restore(self, savepath):
        """
        Signatures need to be re-init after weights are loaded.
        """
        self.embed = tf.saved_model.load(savepath)
        self.init_signatures()



