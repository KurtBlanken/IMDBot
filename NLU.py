import nltk
import NERDb
import re

contractions = {
	"'s" : 'is',
	"n't" : 'not',
	"'re" : 'are',
	"'m" : 'am',
}

nerdb = NERDb.NERDb()

porter = nltk.PorterStemmer()

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
	entitites = set()
	sentence= data['user_utterance']
	
	# get any recognized entities
	entities, pos, neg = nerdb.get_entities_and_prefs(sentence)
	
	data['tagged_words'] = tagged_words
	data['entities'] = entities
	data['pos'] = pos
	data['neg'] = neg
	data['prefs'] = {}
	for (type_name, entity, adj) in pos.union(neg):
		data['prefs'][entity] = adj
	
	data['schema'] = construct_schema(sentence, entities)
	
	act_detect(data)
		
def construct_schema(sentence, entities):
	# construct schema by replacing named entities with type name
	schema = sentence.lower()
	for (type_name, entity, s) in entities:
		schema = schema.replace(s.lower(), type_name, 1)
	return schema

'''
	trivia detection
		search schema for keywords matching trivia patterns
		use best match as trivia
'''	
def act_detect(data):
	best = []
	for keys, t in trivia_patterns:
		matches = [key for key in keys if key in data['schema']]
		if len(matches) >= 1:
			best.append((len(matches), t))
	best.sort(key=lambda x:x[0], reverse=True)
	if len(best) > 0:
		data['act'] = 'trivia'
		data['trivia'] = best[0][1]
	else:
		data['act'] = 'pref'
		
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
		
if __name__ == '__main__':
	s = raw_input("> ")
	data = {
		'user_utterance' : s
	}
	NLU(data)
	print data
