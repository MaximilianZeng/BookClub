# from flask import g # global vars; stored per-session, so not very useful
import pickle

def load_data():
    return {
        'works': load_works(),
        'inverted_index': load_inverted(),
        'tfidf': load_tfidf(),
        'authors': load_authors()
    }

def load_works():
    with open('./data/workid_to_book_info', 'rb') as f:
        data = pickle.load(f)
    return data

def load_inverted():
    with open('./data/NEW_500_SVD_inverted_index_k=200_mintf=0_mindf=0.8_maxdf=0.99', 'rb') as f:
        data = pickle.load(f)
    return data

def load_tfidf():
    with open('./data/NEW_500_SVD_work_tfidf_vecs_k=200_mintf=0_mindf=0.8_maxdf=0.99', 'rb') as f:
        data = pickle.load(f)
    return data

def load_authors():
    with open('./data/author_ind_to_name', 'rb') as f:
        data = pickle.load(f)
    return data
