import sys
import random
user_prefs = {}

def DM(data):
	# initialize prefs for user if they don't exist yet
	if data['id'] not in user_prefs:
		user_prefs[data['id']] = { 'pos' : set(), 'neg' : set(), 'prefs' : {}, 'recs' : get_initial_recs(data)}
	data['recs'] = user_prefs[data['id']]['recs']
	if data['act'] == 'pref':
		update_recommendations(data)
		# update old preferences with the new
		user_prefs[data['id']]['pos'].update(data['pos'])
		user_prefs[data['id']]['neg'].update(data['neg'])
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
	
def get_initial_recs(data):
	recs = [line.split(" ", 1) for line in open('data/top100.txt').readlines()]
	recs = [(long(id), title.strip(), 0) for id, title in recs]
	recs.sort(key=lambda x: x[2], reverse=True)
	return recs

def update_recommendations(data):
	pass
	 
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
					
def when(data):
	for entity in data['entities']:
		if entity[0] == 'PERSON':
			data['outputs'].append("I don't know when {0} was born.".format(get_name(data, entity)))
		elif entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			data['outputs'].append("{0} was made in {1}.".format(m['title'], m['production_year']))
		elif t == 'GENRE':
			data['outputs'].append("I don't know when {0} started, it's a genre.".format(entity[1]))

def director(data):
	for entity in data['entities']:
		if entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			for director in m['directors']:
				data['outputs'].append("{0} directed {1}".format(director['name'], m['title']))

def producer(data):
	for entity in data['entities']:
		if entity[0] == 'MOVIE':
			m = data['imdbi'].get_movie(entity[1])
			for director in m['producers']:
				data['outputs'].append("{0} produced {1}".format(director['name'], m['title']))

def plot(data):
	for t, id in data['entities']:
		if t == 'MOVIE':
			m = data['imdbi'].get_movie(id)
			if len(m['plot']) == 0:
				data['outputs'].append("I don't know the plot of {0}".format(m['title']))
			for line in m['plot']:
				data['outputs'].append(line)
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
	data['outputs'].append("I can't count yet...")
	
def recent(data):
	data['outputs'].append("I can't get you recent things just yet...")
	
def get_name(data, entity):
	t, id = entity
	if t == 'PERSON':
		return data['imdbi'].get_person(id)['name']
	elif t == 'MOVIE':
		return data['imdbi'].get_movie(id)['title']
	elif t == 'GENRE':
		return id
