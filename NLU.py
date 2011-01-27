import nltk
import cPickle

# Saved tagger
tagger_file = open('tagger.pkl', 'rb')
tagger = cPickle.load(tagger_file)
tagger_file.close()

contractions = {
	"'s" : 'is',
	"n't" : 'not',
	"'re" : 'are',
	"'m" : 'am',
}

# Remove contractions from word
# return word
def uncontract(word):
	if word in contractions:
		return contractions[word]
	return word

# Query the database for named entities associated with tagged sentence
# Return a list of entities
def entity_recognition(tagged_words):
	return []

# Classify the dialog act of a sentence
# Replace named entities with object/class label to form meta-sentence
# Return act classification, along with any extra info
def classify_dialog_act(tagged_words, entities):
	return 'unknown'
	
def get_meaning(utterance):
	# uncontract and tokenize utterance
	words = [uncontract(word) for word in nltk.word_tokenize(utterance)]
	# tag words with saved tagger
	tagged_words = tagger.tag(words)
	# get any recognized entities
	entities = entity_recognition(tagged_words)
	# classify the dialog act
	act = classify_dialog_act(tagged_words, entities)
	return {
		'utterance' : utterance,
		'tagged_words' : tagged_words,
		'entities' : entities,
		'act' : act,
	}
