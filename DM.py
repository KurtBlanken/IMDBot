'''
Steven: Ok changed some stuff, if giving errors put something here to let me know.
'''
import sys
import random
import cPickle
import Netflix
import rec_get_diff
user_prefs = {}

was_temp = ["Yes.",
				"Yes, {0} was in {1}",
			  ]
when_temp = ["{0} was made in {1}.",
				 "The production year for {0} was {1}.",
				]
director_temp = ["{0} directed {1}",
					  "{0} was the director of {1}",
					  "I think the director of {0} was {1}",
					 ]

producer_temp = ["{0} produced {1}",
					  "{0} was the producer of {1}",
					 ]
count_temp = ["{0} acted in {1} movies.",
				  "{0} starred in {1} movies.",
				  "{0} was in {1} movies.",
				 ]
			 
actor_temp = ["{0} played {1}.",
				 "{0} was {1} in {2}.",
				]

other_person_temp = ["{0} was a {1} for {2}",
					"{0} was a {1} in {2}",
						  ]

def DM(data):
	# initialize prefs for user if they don't exist yet
	if data['id'] not in user_prefs:
		user_prefs[data['id']] = {
			'pos' : set(),
			'neg' : set(),
			'prefs' : {},
			'recs' : get_initial_recs(),
			'last_prefs' : set(),
		}
	data['recs'] = user_prefs[data['id']]['recs']
	data['last_prefs'] = user_prefs[data['id']]['last_prefs']
	if data['act'] == 'pref':
		old_prefs = [user_prefs[data['id']]['pos'], user_prefs[data['id']]['neg']]
		for pref in data['pos']:
			update_recommendations(data, pref, old_prefs)
		# update old preferences with the new
		user_prefs[data['id']]['pos'].update(data['pos'])
		user_prefs[data['id']]['neg'].update(data['neg'])
		user_prefs[data['id']]['last_prefs'] = set()
		user_prefs[data['id']]['last_prefs'].update(data['pos'])
		user_prefs[data['id']]['last_prefs'].update(data['neg'])
		for key, reason in user_prefs[data['id']]['prefs'].items():
			data['prefs'][key] = reason
		for entity in data['pos']:
			data['outputs'].append("I'm glad you liked {0}.".format(get_name(data, entity)))
		for entity in data['neg']:
			data['outputs'].append("I'm sorry you didn't like {0}.".format(get_name(data, entity)))
	elif data['act'] == 'trivia':
		trivia(data)
	# update current preferences with the old
	data['pos'] = user_prefs[data['id']]['pos']
	data['neg'] = user_prefs[data['id']]['neg']
	
def get_introduction():
	return "Welcome to IMDBot"
	
def get_initial_recs():
	recs = [line.split(" ", 1) for line in open('data/top100.txt').readlines()]
	# changed from tuple to list for assignment
	recs = [[long(id), title.strip(), 0] for id, title in recs] 
	return recs

def update_recommendations(data, entity, old_prefs):
	REC_LEN = 100
	ACTOR_VAL = 15
	GENRE_VAL = 20
	DIRECTOR_VAL = 25
	WRITER_VAL = 30
	movies_to_add = []
	# preferences
	# clear old prefs from the new pref list
	if entity in old_prefs[0]:
		data['pos'].remove(entity)
	if entity in old_prefs[1]:
		data['neg'].remove(entity)
	
	if entity[0] == 'PERSON':
		person = update_actor(data['imdbi'], entity, data['recs'], ACTOR_VAL)
		# add movies to rec list
		for movieID in person['actor']:
			movie = data['imdbi'].get_movie(movieID, cast_info=False, aka_info=False)
			#print movie['id'],'\t',movie['title']
			if movie['id'] == data['recs'][1][0]:
				break
			movies_to_add.append([movie['id'], movie['title'], ACTOR_VAL])
			####
			# How do I tell between a director and a writer or actor?
			####
		if 'director' in person:
			print person['name'],' as a director!'
		if 'writer' in person:
			print person['name'],' as a writer!'
	elif entity[0] == 'GENRE':
		for movie in data['recs']:
			m = data['imdbi'].get_movie(movie[0], cast_info=False, aka_info=False)
			if 'genres' in m and entity[1] in m['genres']:
				movie[2] += GENRE_VAL
	elif entity[0] == 'MOVIE':
		print 'Movie update start'
		movieEntity = data['imdbi'].get_movie(entity[1])#, cast_info=False, aka_info=False)
		new_movies = Netflix.similar_movies(movieEntity['title'], data['imdbi'])	
		new_movies = rec_get_diff.get_top_x(movieEntity,new_movies)
		for movie,title,rating in data['recs']:
			if movie in new_movies[0]:
				data['recs'].remove([movie,title,rating])
		movies_to_add.extend(new_movies)
				
	# update new stuff with old prefs
	for pref in old_prefs[0]:
		if pref[0] == 'PERSON':
			update_actor(data['imdbi'], pref, movies_to_add, ACTOR_VAL)
		elif pref[0] == 'GENRE':
			for movie in data['recs']:
				m = data['imdbi'].get_movie(movie[0], cast_info=False, aka_info=False)
				if 'genres' in m and entity[1] in m['genres']:
					movie[2] += GENRE_VAL
				
	# CULL
	data['recs'].extend(movies_to_add)
	data['recs'].sort(key=lambda x: x[2], reverse=True)
	del data['recs'][REC_LEN:]

def update_actor(imdbi, entity, movies, ACTOR_VAL):
	person = imdbi.get_person(entity[1])
	# if person is an actor
	if 'actor' in person:
		# change confidence for rec list
		for movie in movies:
			movieID = movie[0]
			if movieID in person['actor']:
				movie[2] += ACTOR_VAL
	return person
	 
def trivia(data):
	# dynamically direct the function call based on the trivia type
	# to introduce a new type, just create a function with the same name
	module = sys.modules[globals()['__name__']]
	trivia = data['trivia'].split('_')
	handler = trivia[0]
	args = trivia[1:]
	if handler in module.__dict__:
		if len(args) > 0:
			module.__dict__[handler].__call__(data, args)
		else:
			module.__dict__[handler].__call__(data)
	else:
		data['outputs'].append("Unknown dialog act: {0}".format(data['trivia']))

def was(data, roles):
	data['outputs'] = ["No."]
	for entity1 in data['entities']:
		for entity2 in data['entities']:
			if entity1 != entity2 and entity1[0] == 'PERSON' and entity2[0] == 'MOVIE':
				if is_person_in_movie(data, entity1[1], entity2[1], roles=roles):
					data['outputs'] = ["Yes."]
def role(data):
	for entity1 in data['entities']:
		for entity2 in data['entities']:
			if entity1 != entity2 and entity1[0] == 'PERSON' and entity2[0] == 'MOVIE':
				p = data['imdbi'].get_person(entity1[1])
				m = data['imdbi'].get_movie(entity2[1])
				answer = 'not found.'
				for cast in m['cast']:
					if cast['person_id'] == entity1[1]:
						if cast['role_type'] == 'actor' or cast['role_type'] == 'actress':
							answer = 'actor'
							charname = 'a minor role'
							if 'person_role_id' in cast:
								data['imdbi'].cur.execute('select name from char_name where id = {0}'.format(cast['person_role_id']))
								temp = data['imdbi'].cur.fetchall()
								if len(temp)!=0:
									charname = temp[0][0]
						else:
							answer = cast['role_type']
				if answer == 'not found.':
					data['outputs'].append("{0} didn't have anything to do with {1}.".format(p['name'], m['title']))
				elif answer == 'actor':
					data['outputs'].append(random.choice(actor_temp).format(p['name'], charname, m['title']))
				elif answer == 'director':
					data['outputs'].append(random.choice(director_temp).format(p['name'], m['title']))
				elif answer == 'producer':
					data['outputs'].append(random.choice(producer_temp).format(p['name'],m['title']))
				else:
					data['outputs'].append(random.choice(other_person_temp).format(p['name'], answer, m['title']))

def when(data):
	for entity in data['entities']:
		if entity[0] == 'PERSON':
			data['imdbi'].cur.execute("select info from person_info where person_id = {0} and info_type_id = 41".format(entity[1]))
			date = data['imdbi'].cur.fetchall()
			if len(date) != 0:
				data['outputs'].append("{0} was born {1}.".format(get_name(data, entity), date[0][0]))
			else:
				data['outputs'].append("I don't know when {0} was born.".format(get_name(data,entity)))
		elif entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			data['outputs'].append(random.choice(when_temp).format(m['title'], m['production_year']))

		elif entity == 'GENRE':
			data['outputs'].append("I don't know when {0} started, it's a genre.".format(entity[1]))

def director(data):
	for entity in data['entities']:
		if entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			for director in m['directors']:
				data['outputs'].append(random.choice(directed_temp).format(director['name'], m['title']))

def producer(data):
	for entity in data['entities']:
		if entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			for director in m['producers']:
				data['outputs'].append(random.choice(produced_temp).format(director['name'], m['title']))

def plot(data):
	for t, id in data['entities']:

		if t == 'MOVIE':
			m = data['imdbi'].get_movie(id)
			if len(m['plot']) == 0:
				data['outputs'].append("I don't know the plot of {0}".format(m['title']))
			for plot_desc in m['plot']:
				data['outputs'].append(plot_desc)
	data['outputs'] = random.sample(data['outputs'], 1)

def is_person_in_movie(data, person_id, movie_id, roles=[]):
	movie = data['imdbi'].get_movie(movie_id)
	if not roles:
		return person_id in [person['person_id'] for person in movie['cast']]
	for role in roles:
		if person_id in [person['person_id'] for person in movie[role]]:
			return True
	return False
	
def count(data, things):
	for t, id in data['entities']:
		if t == 'PERSON':
			p = data['imdbi'].get_person(id)
			if 'actor' in p:
				data['outputs'].append(random.choice(count_temp).format(p['name'], len(p['actor'])))
			if 'actress' in p:
				data['outputs'].append(random.choice(count_temp).format(p['name'], len(p['actress'])))

'''
The recent function is kind of weird right now, I'm returning the three movies with the biggest movie_id number (best way I can think of without resorting to massive SQL queries to find most recent movies). The movies are filtered by genre if genre is given in the form of "!Comedy" for excluding a comedy from the list, or "Action" and it will only returns films fit that genre.
'''

def recent(data, genres=[]):
	if not genres:
		role = 'actor'
		genre = ''
	else:
		if len(genres) == 1:
			role = genres[0]
			genre = ''
		elif len(genres) == 2:
			role = genres[0]
			genre = genres[1]
			filter = 'Action'
			for t, g in data['entities']:
				if t == 'GENRE':
					filter = g
	for t, id in data['entities']:
		if t == 'PERSON':
			p = data['imdbi'].get_person(id)
			l = []
			if role == 'actor':
				if 'actor' in p:
					for m in p['actor']:
						l.append(m)
				if 'actress' in p:
					for m in p['actress']:
						l.append(m)
			else:
				if role in p:
					for m in p[role]:
						l.append(m)
			l.sort()
			max = len(l)
			if genre:
				if 'not' in genre:
					genre = filter
					for m in l:
						mov = data['imdbi'].get_movie(m, movie_info=False, aka_info=False, cast_info=False)
						if genre in mov['genres']:
							l.remove(m)
				else:
					genre = filter
					nl = []
					for m in l:
						mov = data['imdbi'].get_movie(m,movie_info=False,aka_info=False,cast_info=False)
						if genre in mov['genres']:
							nl.append(m)
					nl.sort()
					data['outputs'].append(nl)
					l=nl
			if len(l) != 0:
				m_ids = l[-3:]
				data['outputs'].append("Here are some of the movies that might fit your description:")
				for m in m_ids:
					mov = data['imdbi'].get_movie(m,movie_info=False,aka_info=False,cast_info=False)
					data['outputs'].append((mov['title']))
			else:
				data['outputs'].append("I can't get you recent things for {0}".format(p['name']))

def runtime(data):
	for entity in data['entities']:
		if entity[0] == "MOVIE":
			data['imdbi'].cur.execute("select info from movie_info where movie_id = {0} and info_type_id = 1".format(entity[1]))
			gross = data['imdbi'].cur.fetchall()
			if len(gross) !=0:
				data['outputs'].append("{0} had a runtime of {1}".format(get_name(data,entity), gross[0][0]))
			else:
				data['outputs'].append("I don't know how long {0} was.".format(get_name(data,entity)))

def gross(data):
	for entity in data['entities']:
		if entity[0] == "MOVIE":
			data['imdbi'].cur.execute("select info from movie_info where movie_id = {0} and info_type_id = 213".format(entity[1]))
			gross = data['imdbi'].cur.fetchall()
			if len(gross) !=0:
				data['outputs'].append("{0}'s gross revenue was {1}".format(get_name(data,entity), gross[0][0]))
			else:
				data['outputs'].append("I don't know how much money {0} has made.".format(get_name(data,entity)))

def budget(data):
	for entity in data['entities']:
		if entity[0] == 'MOVIE':
			data['imdbi'].cur.execute("select info from movie_info where movie_id = {0} and info_type_id = 209".format(entity[1]))
			gross = data['imdbi'].cur.fetchall()
			if len(gross) !=0:
				data['outputs'].append("{0}'s budget was {1}".format(get_name(data,entity), gross[0][0]))
			else:
				data['outputs'].append("I don't know how much money {0} took to film.".format(get_name(data,entity)))

def erase(data):
	data['pos'] = set()
	data['neg'] = set()
	user_prefs[data['id']]['pos'] = set()
	user_prefs[data['id']]['neg'] = set()
	data['outputs'].append("Ok, sorry.")
	
def get_name(data, entity):
	t, id = entity
	if t == 'PERSON':
		return data['imdbi'].get_person(id)['name']
	elif t == 'MOVIE':
		return data['imdbi'].get_movie(id)['title']
	elif t == 'GENRE':
		return id

def test():
	import imdbi
	pos = [('MOVIE', 614757),("PERSON", 386467),('GENRE','Action')]# 
	data = {
		'pos' : set(pos),
		'neg' : set(),
		'prefs' : {},
		'recs' : get_initial_recs(),
		'imdbi' : imdbi.IMDBInterface(),
		'id' : 'James',
		'act' : 'pref',
		'outputs' : [],
	}
	DM(data)
	for rec in data['recs'][:20]:
		print rec

if __name__ == '__main__':
	test()
