# from flask import g # global vars; stored per-session, so not very useful
import pickle

def load_data():
    return {
        'works': load_works(),
        'work_mat': load_work_mat(),
        'auth_mat': load_auth_mat(),
        'authors': load_authors()
    }

def load_works():
    with open('./data/work_ind_to_book_info', 'rb') as f:
        data = pickle.load(f)
    return data

def load_work_mat():
    with open('./data/work_mat', 'rb') as f:
        data = pickle.load(f)
    return data

def load_auth_mat():
    with open('./data/auth_mat', 'rb') as f:
        data = pickle.load(f)
    return data

def load_authors():
    with open('./data/author_ind_to_name', 'rb') as f:
        data = pickle.load(f)
    return data
