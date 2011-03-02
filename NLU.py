import nltk
import NERDb
from Ontology import *

contractions = {
	"'s" : 'is',
	"n't" : 'not',
	"'re" : 'are',
	"'m" : 'am',
}

nerdb = NERDb.NERDb()

# Remove contractions from word
# return word
def uncontract(word):
	if word in contractions:
		return contractions[word]
	return word

# Query the database for named entities associated with tagged sentence
# Return a list of entities
def entity_recognition(tagged_words):
	entities = set()
	for word, tag in tagged_words:
		entity = find_entity(word, tag, tagged_words)
		if entity != None:
			entities.add(entity)
	return entities

# Classify the dialog act of a sentence
# Replace named entities with object/class label to form meta-sentence
# Return act classification, along with any extra info
def classify_dialog_act(tagged_words, entities):
	return 'pref'
	
def NLU(data):
	# uncontract and tokenize utterance
	words = [uncontract(word) for word in nltk.word_tokenize(data['user_utterance'])]
	# tag words with saved tagger
	tagged_words = nltk.pos_tag(words)
	# get any recognized entities
	#entities = entity_recognition(tagged_words)
	entities= nerdb.get_entities(data['user_utterance'])
	# classify the dialog act
	act = classify_dialog_act(tagged_words, entities)
	data['tagged_words'] = tagged_words
	data['entities'] = entities
	data['act'] = act
	if act == 'pref':
		add_preferences(data)

def add_preferences(data):
	data['prefs'] = data['prefs'].union(data['entities'])
