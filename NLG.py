import random, re
#from imdbi import IMDBInterface


def NLG(data):

  if data['act'] == 'pref':
    handle_pref(data)
  elif data['act'] == 'trivia':
    handle_trivia(data)
  #elif data['act'] == 'chat':
   # handle_chat(data)
  #elif data['act'] == 'rec':
   # handle_rec(data)
  else:
    data['output'] = "I don't know"


#handles pos and neg prefs for actors, genres, and movies
def handle_pref(data):
	imdbi = data['imdbi']
	data['output']=''
	# pos and neg are sets of tuples
	for (type,id) in data['pos']:
	  #pospref=pref
	  if type=='actor':     
	    data['output'] = random.choice(['Yeah ' + str(imdbi.get_person(id)) + ' is ' + str(data['prefs'][id]), 'I agree', 'Ok'])
	  elif type=='movie':
	    data['output'] = random.choice(['You\'re right, ' + str(imdbi.get_movie(id)['title']) + ' is awesome!',
	    'Yeah, I like it too.', 'Ok'])
	  elif type=='genre':
	    data['output'] = random.choice(['I\'m not a big fan of ' + str(id), 'I see.'])
	  else:
	    data['output'] = 'I don\'t know what you are talking about.'
	for (type,id) in data['neg']:
	  #negpref=pref
	  if type == 'actor':
	
	    data['output'] = random.choice(['Yeah, ' + str(imdbi.get_person(id)) + ' is ' + str(data['prefs'][id]), 'Interesting.'])
	  elif type == 'movie':
	    data['output'] = 'You\'re right, ' + str(imdbi.get_movie(id)['title']) + ' is ' + str(data['prefs'][id])
	  elif type == 'genre':
	    data['output'] = 'I\'m not a big fan of ' + str(id)
	  else:
	    data['output'] = 'Huh?'
    

#handles in, when, plot, role, director, producer
def handle_trivia(data):
	answer= data['trivia']['answer']
	imdbi = data['imdbi']
	data['output']= ''
	if data['trivia']['attr'] == 'in':
	  if data['trivia']['answer'] == False:
	    data['output'] = 'No.'
	  elif data['trivia']['answer'] == True:
	    data['output'] = 'Yes.'
	  else:
	    count = 0
	    for person in data['trivia']['answer']:
	      data['output'] = data['output'] + ', ' + str(person)
	      count = count + 1
	      if count == 5:
	        break
	elif data['trivia']['attr'] == 'when':
	  data['output'] = random.choice(['The production year was {0}.'.format(data['trivia']['answer']), str(data['trivia']['answer'])])
	elif data['trivia']['attr'] == 'plot':
	  data['output'] = 'Here\'s the plot: \n' + str(data['trivia']['answer'])
	elif data['trivia']['attr'] == 'role':
	  data['output'] = random.choice([str(imdbi.get_person(data['entities'][0][1])) + ' played ' + str(data['trivia']['answer']), str(data['trivia']['answer'])])
	elif data['trivia']['attr'] == 'director':
		
		directors= ''
		if len(answer) == 2:
			directors= "{0} and {1}".format(answer[0], answer[1])
		else:
			directors= ', '.join(data['trivia']['answer'])
		
		data['output']= directors + ' directed that.'
	elif data['trivia']['attr'] == 'producer':
		
		producers = ''
		if len(answer) == 2:
			producers= "{0} and {1}".format(answer[0], answer[1])
		else:
			producers= ', '.join(data['trivia']['answer'])
		data['output']= producers + ' produced that.'


#def handle_chat(data):
 # data['output'] = 'chat stuff goes here'

#def handle_rec(data):
 # data['output'] = 'rec stuff goes here'

