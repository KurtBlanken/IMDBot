import netflix
import imdbi
import Levenshtein as lev

flix = netflix.Netflix(key='yeg7egk8nyfntnrwf3kghj9e', secret='vc4SrK5eVu', application_name='IMDBot')
# a = imdbi.IMDBInterface()

def similar_movies(title, a):
	catalog_item = flix.request('/catalog/titles/', term=title, max_results=1)[0]
	similar_titles = [(item['title']['regular'], item['release_year']) for item in catalog_item.links['similars'].get(flix)['similars']['similars_item']]
	similars = []
	for title, year in similar_titles:
		title_query = '%{0}%'.format('%'.join(title.split(' '))).replace("'", "\\'")
		a.cur.execute("SELECT id, title, production_year FROM title WHERE title LIKE '{0}'".format(title_query))
		res = a.cur.fetchall()
		matches = []
		for id, _title, _year in res:
			if long(year) == _year:
				matches.append((lev.ratio(str(title), _title), id))
		matches.sort(key=lambda x: x[0], reverse=True)
		if len(matches) > 0:
			similars.append(a.get_movie(matches[0][1]))
	return similars

if __name__ == '__main__':
	title = raw_input('> ')
	print [movie['title'] for movie in similar_movies(title)]
