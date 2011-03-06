import random
from imdbi import IMDBInterface

def NLG(data):
  imdbi = IMDBInterface()
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
  data['output']=''
  for pref in data['pos']:
    pospref=pref
    if pospref[0]=='actor':     
      data['output'] = random.choice(['Yeah ' + str(imdbi.get_person(pospref[1])) + ' is ' + str(data['prefs'][pospref[0], pospref[1]]), 'I agree', 'Ok'])
    elif pospref[0]=='movie':
      data['output'] = random.choice(['You\'re right, ' + str(imdbi.get_movie(pospref[1])) + ' is ' + str(data['prefs'][pospref[0], pospref[1]]),
      'Yeah, I like it too.', 'Ok'])
    elif pospref[0]=='genre':
      date['output'] = random.choice(['I\'m not a big fan of ' + str(pospref[1]), 'I see.'])
    else:
      data['output'] = 'I don\'t know what you are talking about.'
  for pref in data['neg']:
    negpref=pref
    if negpref[0]=='actor':
      data['output'] = random.choice(['Yeah, ' + str(imdbi.get_person(negpref[1])) + ' is ' + str(data['prefs'][negpref[0], negpref[1]]), 'Interesting.'])
    elif negpref[0]=='movie':
      data['output'] = 'You\'re right, ' + str(imdbi.get_movie(negpref[1])) + ' is ' + str(data['prefs'][negpref[0], negpref[1]])
    elif negpref[0]=='genre':
      date['output'] = 'I\'m not a big fan of ' + str(negpref[1])
    else:
      data['output'] = 'Huh?'
    
#handles in, when, plot, role, director, producer
def handle_trivia(data):
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
  if data['trivia']['attr'] == 'when':
    data['output'] = random.choice(['The production year was {0}.'.format(data['trivia']['answer']), str(data['trivia']['answer'])])
  if data['trivia']['attr'] == 'plot':
    data['output'] = 'Here\'s the plot: \n' + str(data['trivia']['answer'])
  if data['trivia']['attr'] == 'role':
    data['output'] = random.choice([str(imdbi.get_person(data['entities'][0][1])) + ' played ' + str(data['trivia']['answer']), str(data['trivia']['answer'])])
  if data['trivia']['attr'] == 'director':
    data['output'] = str(imdbi.get_person(data['trivia']['answer'])) + ' directed that.'
  if data['trivia']['attr'] == 'producer':
    data['output'] = str(imdbi.get_person(data['trivia']['answer'])) + ' was the producer.'


#def handle_chat(data):
 # data['output'] = 'chat stuff goes here'

#def handle_rec(data):
 # data['output'] = 'rec stuff goes here'
