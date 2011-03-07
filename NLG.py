import random
from imdbi import IMDBInterface

def NLG(data):
  imdbi = IMDBInterface()
  if data['act'] == 'pref':
    handle_pref(data)
  elif data['act'] == 'trivia':
    handle_trivia(data)
  elif data['act'] == 'chat':
    handle_chat(data)
  else:
    data['output'] = "I don't know."

#handles pos and neg prefs for actors, genres, and movies
def handle_pref(data):
  data['output'] = ''
  for pref in data['pos'].union(data['neg']):
    data['output'] = random.choice([
      'I agree.',
      'Ok.',
    ])
    
#handles in, when, plot, role, director, producer
def handle_trivia(data):
  data['output'] = ''
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


def handle_chat(data):
  data['output'] = 'chat stuff goes here'
