import nltk
import NERDb, DM
from Ontology import *

contractions = {
	"'s" : 'is',
	"n't" : 'not',
	"'re" : 'are',
	"'m" : 'am',
}

nerdb = NERDb.NERDb()

porter= nltk.PorterStemmer()

prefs = [line.strip() for line in open('data/preferences.txt').readlines() if len(line.strip()) > 0]
pos = set(prefs[prefs.index("# pos")+1:prefs.index("# neg")])
neg = set(prefs[prefs.index("# neg")+1:])
trivia_patterns = open('data/trivia_patterns.txt').readlines()
trivia_patterns = [pat.split("|") for pat in trivia_patterns]
trivia_patterns = [([key.strip() for key in keys.split(",")], t.strip()) for (keys, t) in trivia_patterns]

# remove contractions from word
def uncontract(word):
	if word in contractions:
		return contractions[word]
	return word
	
def NLU(data):
	# uncontract and tokenize utterance
	words = [uncontract(word) for word in nltk.word_tokenize(data['user_utterance'])]
	# tag words with saved tagger
	tagged_words = nltk.pos_tag(nltk.word_tokenize(data['user_utterance']))
	entitites= set()
	sentence= data['user_utterance']
	
	# get any recognized entities
	entities = nerdb.get_entities(sentence)
	data['tagged_words'] = tagged_words
	data['entities'] = map(lambda (type_name, id, s): (type_name, id), entities)
	
	# add entity to pos and neg preference set
	data['pos'] = set()
	data['neg'] = set()
	data['prefs'] = {}
	
	tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
	
	for (word, tag) in tagged:
		if tag.find('VB') != -1 or tag == 'JJ':
			stem = porter.stem(word)
			if stem in pos or word in pos:
				for (type_name, entity) in data['entities']:
					data['pos'].add((type_name, entity))
					data['prefs'][entity] = word
					data['act'] = 'pref'
			elif stem in neg or word in neg:
				for (type_name, entity) in data['entities']:
					data['neg'].add((type_name, entity))
					data['prefs'][entity] = word
					data['act'] = 'pref'
	
	# construct schema by replacing named entities with type
	schema = sentence.lower()
	for (type_name, entity, s) in entities:
		assert s in schema
		schema = schema.replace(s, type_name, 1)
	data['schema'] = schema
	if data['act'] == None:
		trivia_detect(data)

'''
	trivia detection
		search schema for keywords matching trivia patterns
		use best match as trivia
'''	
def trivia_detect(data):
	best = []
	for keys, t in trivia_patterns:
		matches = [key for key in keys if key in data['schema']]
		if len(matches) >= 1:
			best.append((len(matches), t))
	best.sort(key=lambda x:x[0], reverse=True)
	if len(best) > 0:
		data['act'] = 'trivia'
		data['trivia'] = best[0][1]
		
def add_entity_names(data):
	data['entity_names'] = {}
	for t, id in set(data['entities']).union(data['pos']).union(data['neg']):
		name = None
		if t == 'PERSON':
			name = data['imdbi'].get_person(id)['name']
		elif t == 'MOVIE':
			name = data['imdbi'].get_movie(id)['title']
		elif t == 'GENRE':
			name = id
		data['entity_names'][id] = name
