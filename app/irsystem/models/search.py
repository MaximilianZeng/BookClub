import math
import json
from collections import defaultdict
import numpy as np
def cosine_similarity(joined_queries, eligible, work_mat, auth_mat, positive_query_works, query_works, positive_query_authors):
    """Returns a list of work ids ranked by similarity to a query. Does not use formal cosine similarity due to the omission of normalizing by the doc norm. 

    Arguments
    =========

    joined_queries: np matrix,
        A vector representing the joined queries and author preferences

    Returns
    ======
    ranked_results: list of size len(tf_idf_vectors)
        ranked_results[i] = work id of the i'th most relevant work
    """
    results = []
    similarity_scores = np.matmul(work_mat, joined_queries)
    for i in np.argsort(-similarity_scores):
        if i in eligible and i not in query_works:
            results.append((i, similarity_scores[i]))
        if len(results)==100:
            break
    if len(positive_query_works) == 0 and len(positive_query_authors) == 0:
        return results       

    reordered_results = []
    for work, score in results:
        cosine_sims = []
        for query in positive_query_works:
            cosine_sims.append(np.dot(work_mat[query], work_mat[work]))
        for query in positive_query_authors:
            cosine_sims.append(np.dot(auth_mat[query], work_mat[work]))
        reordered_results.append((work, np.min(np.array(cosine_sims))))
        reordered_results.sort(key=lambda x: x[1], reverse=True)
    return reordered_results


def combine_queries(work_ids, auth_ids, work_mat, auth_mat):
    """

    Arguments
    =========

    work_ids: list,
        A list of works and their scores in the query
        
    
    Returns
    ======
    query: dict mapping terms to tf-idf values
    """
    dimensions = len(work_mat[0])
    combined_queries = np.zeros(dimensions)
    for query_work in work_ids:
        weight = query_work["score"]
        vector_id = query_work["work_id"]
        combined_queries += work_mat[vector_id]*weight

    for query_author in auth_ids:
        weight = query_author["score"]
        vector_id = query_author["auth_id"]
        combined_queries += auth_mat[vector_id]*weight

    query_norm = 0
    for val in combined_queries:
        query_norm+=val**2
    query_norm = query_norm**0.5

    if query_norm<0.0000001:
        return combined_queries
    else:
        return combined_queries/query_norm

def get_doc_rankings(work_ids, eligible, auth_ids, work_mat, auth_mat, works):
    """Returns a dictionary of terms and tf-idf values representing the combined result of individual queries

    Arguments
    =========

    work_ids: list,
        A list of works in the query


    Returns
    ======
    results_list: A JSON-formatted list of dictionaries containing K/V pairs for title, author, ranking, book_url, image_url, and description.
    """
    positive_query_works = []
    positive_query_authors = []
    query_works = []
    for query in work_ids:
        if query["score"] > 0:
            positive_query_works.append(query["work_id"])
        query_works.append(query["work_id"])
    for query in auth_ids:
        if query["score"] > 0:
            positive_query_authors.append(query["auth_id"])

    joined_queries = combine_queries(work_ids, auth_ids, work_mat, auth_mat)
    ranked_results = cosine_similarity(joined_queries, eligible, work_mat, auth_mat, positive_query_works, query_works, positive_query_authors)

    final_results_list = []
    for i, result in enumerate(ranked_results[:100]):
        work_data = works[ranked_results[i][0]]
        rankings_data_dict = {
            "title":work_data["title"],
            "author":work_data["author_names"],
            "ranking":i+1,
            "book_url":work_data["url"],
            "image_url":work_data["image"],
            "description":work_data["description"]
        }
        final_results_list.append(rankings_data_dict)
    return final_results_list