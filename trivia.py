
import re

'''
supported attrs:

in, plot, when, role, char, director, producer, produced, directed, acted, recent, last
    
trivia handler, updates the data structer with answers to
trivia questions. takes in nlu_to_dm_test_input and then
append an answer
field to the trivia dictionary.
'''
import random
import imdb
import datetime

dbinfo = eval(open('dbinfo.txt').read())
user = dbinfo['user']
pw = dbinfo['passwd']
db = dbinfo['db']
host = dbinfo['host']
URI = 'mysql://{0}:{1}@{2}/{3}'.format(user,pw,host,db)
imdb_inst = imdb.IMDb('sql', uri = URI)

def handle(data):
	triv = data['trivia']
	if triv['attr'] != '':
		triv_type = triv['attr']
# returns the last three movies an actor or actress filmed
# this function is very slow since it retrives a person object with imdbpy
		if triv_type == 'recent' or triv_type == 'last':
			type, id = data['entities'][0]
			if type != 'person':
				triv['answer'] = "Sorry, please tell me the name a person."
			else:
				person = imdb_inst.get_person(id)
				if 'actress' in person.keys():
				# The three most recent movies are appended onto a list
					cur = 0
					triv['answer'] = list()
					least = now - person['actress'][0]['year']
					for movie in person['actress']:
						cur = cur + 1
						triv['answer'].append(movie['title'])
						if cur > 2:
							break
				elif 'actor' in person.keys():
					cur = 0
					triv['answer'] = list()
					for movie in person['actor']:
						cur = cur + 1
						triv['answer'].append(movie['title'])
						if cur > 2:
							break
		# following types return an integer of how many a 			# person directed, acted, or produced	
		elif triv_type == 'acted':
			type, id = data['entities'][0]
			person = data['imdbi'].get_person(id)
			if 'actor' in person:
				triv['answer'] = len(person['actor'])
			elif 'actress' in person:
				triv['answer'] = len(person['actress'])
			else:
				triv['answer'] = 0
		elif triv_type == 'directed':
			type, id = data['entities'][0]
			person = data['imdbi'].get_person(id)
			if 'director' in person:
				triv['answer'] = len(person['director'])
			else:
				triv['answer'] = 0
		elif triv_type == 'produced':
			type, id = data['entities'][0]
			person = data['imdbi'].get_person(id)
			if 'producer' in person:
				triv['answer'] = len(person['producer'])
			else:
				triv['answer'] = 0
		# returns the role a person was involved with in a movie	
		elif triv_type == 'role':
			p_id = ''
			m_id = ''
			for type, id in data['entities']:
				if type == 'person':
					p_id = id
				elif type == 'movie':
					m_id = id
				if p_id != '' and m_id != '':
					person = data['imdbi'].get_person(p_id)
					movie = data['imdbi'].get_movie(m_id)
					triv['answer'] = "{0} was not related to {1}.".format(person['name'],movie['title'])
					for cast in movie['cast']:
						if cast['person_id'] == p_id:
							if cast['role_type'] == 'actor' or cast['role_type'] == 'actress':
								triv_type = 'char'
							else:
								triv['answer'] = cast['role_type']
		# returns the character name of an actor/actress in a movie
		if triv_type == 'char':
			type1= ''
			type2= ''
			p_id= ''
			m_id= ''
			if len(data['entities']) == 2:
				for entity in data['entities']:
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
							triv['answer'].append('played ')
							triv['answer'].append(name[0][0])
						if 'note' in cast:
								triv['answer'].append(cast['note'])
		elif triv_type == 'producer':
			triv_movies(data, 'producers')
		elif triv_type == 'director':
			triv_movies(data, 'directors')
		elif triv_type == 'plot':
			type, m_id = data['entities'][0]
			if type == 'movie':
				movie = data['imdbi'].get_movie(m_id)
			if len(movie['plot']) != 0:
				triv['answer'] = random.sample(movie['plot'], 1)
			else:
				triv['answer'] = "Ask the plot of a movie please."
		#'in' questions answers true/false
		elif triv_type == 'in':
			type1, p_id = data['entities'][0]
			type2, m_id = data['entities'][1]
			triv_movies(data,'actors')
#'when' function asking for production year
		elif triv_type == 'when':
			type, id = data['entities'][0]
			if type == 'movie':
				mov = data['imdbi'].get_movie(id)
				triv['answer'] = mov['production_year']
			elif type == 'person':
				pers = imdb_inst.get_person(id)
				triv['answer'] = pers['birth date']
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
		who_movie(data, role)
	elif len(data['entities']) == 2:
		type1= ''
		type2= ''
		p_id= ''
		m_id= ''
		for entity in data['entities']:
			if entity[0]== "person":
				type1, p_id= entity
			else:
				type2, m_id= entity
		is_person_in_movie(data, p_id, m_id, role)
	elif len(data['entities']) > 2:
		p_id = ''
		m_id = ''
		final_ans = False
		for type, id in data['entities']:
			if type == 'person':
				p_id = id
			if type == 'movie':
				m_id = id
			if p_id != '' and m_id !='':
				is_person_in_movie(data, p_id, m_id,role)
				if triv['answer'] == True:
					final_ans = True
		triv['answer'] = final_ans		

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
				

# helper function to determine who produced/directed a movie
def who_movie(data, triv_type):
	m_id= None
	answers= []
	if len(data['entities']) == 1:
		#entities is a list of tuples
		m_id= data['entities'][0][1]
	#print m_id
	data['trivia']['answer'] = "I don't know."
	movie = data['imdbi'].get_movie(m_id)
	if triv_type == 'directors':
		if 'directors' in movie:
			# directors is a list of dictionaries
			directors= []
			for director in movie['directors']:
				answers.append(director['name'])
			
			#data['trivia']['answer'] = directors
	elif triv_type == 'producers':
		if 'producers' in movie:
			producers= []
			for producer in movie['producers']:
				answers.append(producer['name'])
			#data['trivia']['answer'] = producers
	# output answers in first last format
	if len(answers) > 0:
		tmp = []
		for answer in answers:
			answer= re.split(r'[,\s]+', answer)
			answer.reverse()
			answer= ' '.join(answer)
			tmp.append(answer)
		data['trivia']['answer']= tmp
