



'''
  supported attrs:
    in, plot, when, role, director, producer
    
  trivia handler, updates the data structer with answers to
  trivia questions. takes in nlu_to_dm_test_input and then append an answer
  field to the trivias dictionary.
'''
import random

def handle(data):
	'''
	for triv in data['trivia']:
		triv['answer'] = list()
		if triv['attr'] != '':
			triv_type = triv['attr']
			#'in' questions answers true/false
			if triv_type == 'in':
				type1= ''
				type2= ''
				p_id= ''
				m_id= ''
				if len(triv['entities']) == 2:
					for entity in triv['entities']:
						if entity[0]== "person":
							type1, p_id= entity
						else:
							type2, m_id= entity
				if type1 == 'person' and type2 == 'movie':
					is_person_in_movie(data, p_id, m_id)
				else:
					triv['answer'] = 'How can a {0} be in a {1}'.format(type1, type2)
      #'when' function asking for production year
			elif triv_type == 'when':
				type, id = triv['entity']
				if type == 'movie':
					mov = data['data['imdbi']'].get_movie(id)
					triv['answer'] = mov['production_year']
				else:
					triv['answer'] = "I don't know about {0}s".format(type)
=======
'''
	triv = data['trivia']
	if triv['attr'] != '':
		triv_type = triv['attr']
		if triv_type == 'role':
			type1= ''
			type2= ''
			p_id= ''
			m_id= ''
			if len(triv['entities']) == 2:
				for entity in triv['entities']:
					if entity[0]== "person":
						type1, p_id= entity
					else:
						type2, m_id= entity
			if type1 == 'person' and type2 == 'movie':
				movie = data['imdbi'].get_movie(m_id)
				triv['answer'] = "Sorry, couldn't find the character."
				for cast in movie['cast']:
					if p_id == cast['person_id'] and 'person_role_id' in cast:
						triv['answer'] = list()
						data['imdbi'].cur.execute('select name from char_name where id = {0}'.format(cast['person_role_id']))
						name = data['imdbi'].cur.fetchall()
						if len(name) != 0:
							triv['answer'].append(name[0][0])
						if 'note' in cast:
								triv['answer'].append(cast['note'])
		if triv_type == 'producer':
			triv_movies(data, 'producers')
		if triv_type == 'director':
			triv_movies(data, 'directors')
		if triv_type == 'plot':
			type, m_id = data['entities'][0]
			if type == 'movie':
				movie = data['imdbi'].get_movie(m_id)
			if len(movie['plot']) != 0:
				triv['answer'] = random.sample(movie['plot'], 1)
			else:
				triv['answer'] = "Ask the plot of a movie please."
		#'in' questions answers true/false
		if triv_type == 'in':
			type1, p_id = data['entities'][0]
			type2, m_id = data['entities'][1]
			triv_movies(data,'actors')
#'when' function asking for production year
		elif triv_type == 'when':
			type, id = triv['entities'][0]
			if type == 'movie':
				mov = data['imdbi'].get_movie(id)
				triv['answer'] = mov['production_year']
			#elif type == 'person':
			#	pers = imdb_triv.get_person(id)
			#	triv['answer'] = pers['birth date']
			else:
				triv['answer'] = "I don't know about {0}s".format(type)
	else:
		data['errors'] = 'no attribute for trivia'
'''
takes in data dict and a role_type
returns everyone who fits the role in a movie if only a movie entity if given
returns true/false if a person did a role in a movie for multiple movies

'''

def triv_movies(data, role):
	triv = data['trivia']
	if len(data['entities']) == 1:
		type, id = data['entities'][0]
		if type == 'movie':
			movie = data['imdbi'].get_movie(id)
			triv['answer'] = list()
			for ppl in movie[role]:
				triv['answer'].append(ppl['name'])
			if role == 'actors':
				for ppl in movie['actresses']:
					triv['answer'].append(ppl['name'])

		else:
			triv['answer'] = "don't know"
	elif len(data['entities']) == 2:
		type1= ''
		type2= ''
		p_id= ''
		m_id= ''
		for entity in triv['entities']:
			if entity[0]== "person":
				type1, p_id= entity
			else:
				type2, m_id= entity
		is_person_in_movie(data, p_id, m_id, role)
	elif len(data['entities']) > 2:
		p_id = 0
		m_id = 0
		final_ans = False
		for type, id in data['entities']:
			if type == 'person':
				p_id = id
			if type == 'movie':
				m_id = id
			if p_id != 0 and m_id !=0:
				is_person_in_movie(data, p_id, m_id,role)
				if triv['answer'] == True:
					final_ans = True
		triv['answer'] = final_ans		


'''<<<<<<< HEAD
#helper function to find if an actor/actress was in a movie
def is_person_in_movie(data, p_id, m_id):
	data['answer'] = False
	movie = interface.get_movie(m_id)
	if 'actors' in movie:
======='''
#helper function to find if an actor/actress was in a movie.
#if a producer produced a movie.
#if a director directed a movie.
def is_person_in_movie(data, p_id, m_id, role_type):
	data['trivia']['answer'] = False
	movie = data['imdbi'].get_movie(m_id)
	if 'actors' in movie and role_type == 'actors':
		for actor in movie['actors']:
			if actor['person_id'] == p_id:
				data['trivia']['answer'] = True
	if 'actresses' in movie and role_type == 'actors':
		for actress in movie['actresses']:
			if actress['person_id'] == p_id:
				data['trivia']['answer'] = True
	elif 'directors' in movie and role_type == 'directors':
		for director in movie['directors']:
			if director['person_id'] == p_id:
				data['trivia']['answer'] = True
	elif 'producers' in movie and role_type == 'producers':
		for producer in movie['producers']:
			if producer['person_id'] == p_id:
				data['trivia']['answer'] = True
