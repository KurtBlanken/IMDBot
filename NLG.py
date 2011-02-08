import random

genre_pref_templates = [
	'I like {0[1]} too.',
	'Ok.',
	"What other genres do you like?",
	'{0[1]} is a good genre.',
]

def NLG(data):
	if data['act'] == 'pref':
		handle_pref(data)
	else:
		data['output'] = "I don't know"
		
def handle_pref(data):
	if not data['errors']:
		for entity in data['entities']:
			if entity[0] == 'genre':
				data['output'] = random.choice(genre_pref_templates).format(entity)
	else:
		data['output'] = 'Errors...'
	data['output'] = data['output'].capitalize()
