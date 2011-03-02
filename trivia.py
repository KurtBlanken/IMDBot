'''
  supported attrs:
    in, plot, when, role, director, producer
    
  trivia handler, updates the data structer with answers to
  trivia questions. takes in nlu_to_dm_test_input and then append an answer
  field to the trivias dictionary.
'''
def handle(data):
	for triv in data['trivias']:
		triv['answer'] = list()
		if triv['attr'] != '':
			triv_type = triv['attr']
			#'in' questions answers true/false
			if triv_type == 'in':
				type1, p_id = triv['entities'][0]
				type2, m_id = triv['entities'][1]
				if type1 == 'person' and type2 == 'movie':
					is_person_in_movie(data, p_id, m_id)
				else:
					triv['answer'] = 'How can a {0} be in a {1}'.format(type1, type2)
      #'when' function asking for production year
			elif triv_type == 'when':
				type, id = triv['entity']
				if type == 'movie':
					mov = data['imdbi'].get_movie(id)
					triv['answer'] = mov['production_year']
				else:
					triv['answer'] = "I don't know about {0}s".format(type)
		else:
			data['errors'] = 'no attribute for trivia'

#helper function to find if an actor/actress was in a movie
def is_person_in_movie(data, p_id, m_id):
	data['answer'] = False
	movie = data['imdbi'].get_movie(m_id)
	if 'actors' in movie:
		for actor in movie['actors']:
			if actor['person_id'] == p_id:
				data['answer'] = True
	elif 'actresses' in movie:
		for actress in movie['actresses']:
			if actress['person_id'] == p_id:
				data['answer'] = True
