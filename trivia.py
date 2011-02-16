#import imdb-iface
#actually import imdb-iface when running against real database
#test

nlu_test_input = {	'act':'trivia',
		'trivias':[
			{	'attr':'in',
				'entities':[('person',260886),('movie',48368)],
			}]
}

#trivia handler, updates the data structer with answers to
#trivia questions. takes in nlu_to_dm_test_input and then append #an answer field to the trivias dictionary.

def handle_triv(data):
	for triv in data['trivias']:
		triv['answer'] = list()
		if triv['attr'] != '':
			triv_type = triv['attr']
			#'in' questions answers true/false
			if triv_type == 'in':
				pid = triv['entities'][0][1]
				mid = triv['entities'][1][1]
				triv['answer'] = pers_in_movie(pid,mid)
                #'when' function asking for production year
			if triv_type == 'when' and triv['entities'][0][0] == 'movie':
				mid = triv['entities'][0][1]
				mov = get_movie(mid)
				triv['answer'] = mov['production_year']
		else:
			data['errors'] = 'no attribute for trivia'


#helper function to find if an actor/actress was in a movie

def pers_in_movie(pers_id, movie_id):
	ans = False
	triv_movie = get_movie(movie_id)
	if 'actors' in triv_movie.keys():
		for actor in triv_movie['actors']:
			if actor['person_id'] == pers_id:
				ans = True
	if 'actresses' in triv_movie.keys():
		for actress in triv_movie['actresses']:
			if actress['person_id'] == pers_id:
				ans = True
	return ans

#delete this get_movie function when testing with imdb-iface.py
#I couldn't connect to SQL so I couldn't fool around with your #function, so I assumed a get_movie function that returns a #simple dictionary mimicking a get_movie.

def get_movie(movie_id):
	dict = {	'movie_id':'48368',
			'production_year':1998,
			'actors':[{'person_id':260886,
					'role_type':'actor',
					'name':'Affleck, Ben'}],}
	return dict

