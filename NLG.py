import random, re
import sys

def NLG(data):
	# dynamically direct the function call based on the dialog act
	# to introduce a new act, just create a function with the same name
	module = sys.modules[globals()['__name__']]
	module.__dict__[data['act']].__call__(data)

#handles pos and neg prefs for actors, genres, and movies
def pref(data):
  data['output'] = ''
  for pref in data['pos'].union(data['neg']):
    data['output'] = random.choice([
      'I agree.',
      'Ok.',
    ])

#handles in, when, plot, role, director, producer
def trivia(data):
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
    data['output'] = random.choice([
    	'The production year was {0}.'.format(
    		data['trivia']['answer'],
    		data['trivia']['answer']),
    ])
  if data['trivia']['attr'] == 'plot':
    data['output'] = "Here's the plot: \n {0}".format(data['trivia']['answer'])
  if data['trivia']['attr'] == 'role':
    data['output'] = random.choice([
    	'{0} played {1}.'.format(imdbi.get_person(data['entities'][0][1]), data['trivia']['answer']),
    ])
  if data['trivia']['attr'] == 'director':
    data['output'] = '{0} directed that.'.format(imdbi.get_person(data['trivia']['answer']))
  if data['trivia']['attr'] == 'producer':
    data['output'] = '{0} was the producer.'.format(imdbi.get_person(data['trivia']['answer']))

def chat(data):
  data['output'] = 'chat stuff goes here'
