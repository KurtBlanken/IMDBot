import random

def NLG(data):
  if data['act'] == 'pref':
    handle_pref(data)
  if data['act'] == 'trivia':
    handle_trivia(data)
  if data['act'] == 'chat':
    handle_chat(data)
#if data['act'] == 'rec':
#handle_pref(data)
  else:
    data['output'] = "I don't know"


def handle_pref(data):
  data['output']=''
  for pref in data['pos']:  
    pospref=pref
    if pospref[0]=='actor':
      data['output'] = 'yeah ' + str(pospref[1]) + ' is ' + str(data['prefs'][pospref[0], pospref[1]])
    if pospref[0]=='movie':
      data['output'] = 'You\'re right, ' + str(pospref[1]) + ' is ' + str(data['prefs'][pospref[0], pospref[1]])
    if pospref[0]=='genre':
      date['output'] = 'I\'m not a big fan of ' + str(pospref[1])
    else:
      data['output'] = 'I don\'t know what you are talking about.'
  for pref in data['neg']:
    negpref=pref
    if negpref[0]=='actor':
      data['output'] = 'Yeah, ' + str(negpref[1]) + ' is ' + str(data['prefs'][negpref[0], negpref[1]])
    if negpref[0]=='movie':
      data['output'] = 'You\'re right, ' + str(negpref[1]) + ' is ' + str(data['prefs'][negpref[0], negpref[1]])
    if negpref[0]=='genre':
      date['output'] = 'I\'m not a big fan of ' + str(negpref[1])
    else:
      data['output'] = 'Huh?'
    
#based on test_cases.py
def handle_trivia(data):
  data['output']= ''
  if data['trivia']['attr'] == 'in':
    if data['trivia']['answer'] == False:
      data['output'] = 'No.'
    if data['trivia']['answer'] == True:
      data['output'] = 'Yes.'
  if data['trivia']['attr'] == 'when':
    data['output'] = 'The production year was ' + str(data['trivia']['answer'])


def handle_chat(data):
  data['output'] = 'chat stuff goes here'

def handle_rec(data):
  data['output'] = 'rec stuff goes here'
