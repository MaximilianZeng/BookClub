from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app import app as data_pool
import json
from app.irsystem.models.search import get_doc_rankings
#import os
#import psutil
project_name = "Book Club"
net_id = "Caroline Lui: cel243, Elisabeth Finkel: esf76, Janie Walter: jjw249, Kurt Huebner: krh57, Taixiang(Max) Zeng: tz376"

# def memory_usage_psutil():
# 	# return the memory usage in MB
# 	process = psutil.Process(os.getpid())
# 	print(process.memory_info().rss/float(2 ** 20))

### helpers ###
def _get_book_from_partial(book_str):
	"""Given a partial string `book_str`, returns a list of elements 
	("book_name by author", work_id, cover) where book_str is a substring
	of book_name. The HTML template can then use the strings, work_ids, 
	and cover image urls to display possible matches for the user to
	select between.
	"""
	works = data_pool.data['works']
	relv_books = []
	book_str = book_str.lower()
	for work_id in range(len(works)):
		title = works[work_id]['title']
		if book_str in title.lower():
			authors = works[work_id].get("author_names", ["(unknown)"])
			authors = ", ".join(authors)
			string = f'"{title}" by {authors}'
			relv_books.append(
				{"string": string, "work_id": work_id, "image": works[work_id].get("image")}
			)
		if len(relv_books) >= 20:
			break
	return relv_books

def _clean(s):
	""" To clean author names """
	return s.lower().replace(".", "").strip()

def _get_author_from_partial(auth_str):
	"""Given a partial string `auth_str`, returns a list of elements 
	(full_name, auth_id) where auth_id has name full_name and where
	auth_str is a substring of full_name.
	
	The HTML template can then use the strings to display possible matches
	for the user to select between.
	"""
	authors = data_pool.data['authors'] 
	relv_auths = []
	auth_str = _clean(auth_str)
	for i, auth_name in enumerate(authors):
		if auth_str in _clean(auth_name):
			relv_auths.append({"name": auth_name, "author_id": i})
		if len(relv_auths) >= 20:
			break
	return relv_auths

def fake_results():
	return [
		{
			"title": "abc"+str(i),
			"author": "asdfa",
			"ranking": i,
			"book_url": "https://www.goodreads.com/book/show/862041.Harry_Potter_Boxset",
			"image_url": "https://images.gr-assets.com/books/1392579059m/862041.jpg",
			"description": "this book is about..." + "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."*3,
			"genres": ["fantasy", "whatever"]
		}
		for i in range(20)
	]

def rescore(inputs, idid):
	"""Given some inputs in form [{work_id: stars}], rescale and
	return rescored inpust in form [{`idid`: work_id, "score": score}]"""
	rescale = {1: -1.8, 2: -0.9, 3: 0.5, 4: 1, 5: 2}
	rescored = []
	for i in inputs:
		iid, stars = list(i.items())[0]
		if type(iid)==str:
			iid = int(iid)
		if type(stars)==str:
			stars = int(stars)
		rescored.append({idid: iid, "score": rescale.get(stars, 0)})
	return rescored

def _get_reccs(work_ids, auth_ids, desired_genres, excluded_genres):
	works = data_pool.data['works']
	eligible = []
	des, exc = set(desired_genres), set(excluded_genres)
	for i, work in enumerate(works):
		# # Logical AND and logical NOT:
		# if set(work['genres']).issubset(req) and set(work['genres']).isdisjoint(exc):
		# # Logical OR and logical NOT:
		if set(work['genres'])&des and set(work['genres']).isdisjoint(exc):
			eligible.append(i)
		elif len(desired_genres)==0 and set(work['genres']).isdisjoint(exc):
			eligible.append(i)
	# return fake_results() # TODO remove once get_doc_rankings is updated
	return get_doc_rankings(
		work_ids,
		eligible,
		auth_ids,
		data_pool.data['work_mat'],
		data_pool.data['auth_mat'],
		data_pool.data['works']
	)


### ajax endpoints ###

# GET request to search for matching book names
@irsystem.route('/booknames', methods=['GET'])
def get_book_from_partial():
	partial = request.args.get('partial')
	if not partial:
		return json.dumps([])
	return json.dumps(_get_book_from_partial(partial))


# GET request to search for matching author names
@irsystem.route('/authornames', methods=['GET'])
def get_author_from_partial():
	partial = request.args.get('partial')
	if not partial:
		return json.dumps([])
	return json.dumps(_get_author_from_partial(partial))


### html endpoints ###

# Endpoint that receives preferences
@irsystem.route('/result', methods=['POST'])
def get_reccs():
	req = json.loads(request.data)
	works = req.get('works') # list of dicts: [{work_id: 234, stars: 2}, ...]
	works_rescored = rescore(works, "work_id")

	# works_rescored = []
	# for w in works:
	# 	wid, stars = list(w.items())[0]
	# 	if type(wid)==str:
	# 		wid = int(wid)
	# 	if type(stars)==str:
	# 		stars = int(stars)
	# 	works_rescored.append({"work_id": wid, "score": rescale.get(stars, 0)})
	authors = req.get('authors')
	authors_rescored = rescore(authors, "auth_id")
	# authors_rescored = []
	# for a in authors:
	# 	aid, stars = list(a.items())[0]
	# 	if type(aid)==str:
	# 		aid = int(aid)
	# 	if type(stars)==str:
	# 		stars = int(stars)
	# 	authors_rescored.append({"auth_id": aid, "score": rescale.get(stars, 0)})
	req_genres = req.get('required_genres', [])
	ex_genres = req.get('excluded_genres', [])

	print(works_rescored, authors_rescored, req_genres, ex_genres)
	results = _get_reccs(works_rescored, authors_rescored, req_genres, ex_genres)
	# print(results)
	return json.dumps(results)


# Endpoint to redirect to result page
@irsystem.route('/result', methods=['GET'])
def get_result():
	return render_template('result.html'), 200


# Landing page
@irsystem.route('/', methods=['GET'])
def select():
	return render_template('select.html'), 200
