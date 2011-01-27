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
	from nltk.corpus import names
	import random
	names = ([(name, 'male') for name in names.words('male.txt')] +
					 [(name, 'female') for name in names.words('female.txt')])
	random.shuffle(names)
	def gender_features(word):
		return {'last_letter' : word[-1]}
	featuresets = [(gender_features(n), g) for (n,g) in names]
	train_set, test_set = featuresets[500:], featuresets[:500]
	classifier = nltk.NaiveBayesClassifier.train(train_set)
	print classifier.classify(gender_features("Fred"))
	print classifier.classify(gender_features("Trinity"))
	
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
