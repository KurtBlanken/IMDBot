import nltk
import cPickle

tagger_file = open('tagger.pkl', 'rb')
tagger = cPickle.load(tagger_file)
tagger_file.close()

contractions = {
	"'s" : 'is',
	"n't" : 'not',
	"'re" : 'are'
}

def uncontract(word):
	if word in contractions:
		return contractions[word]
	return word

def get_meaning(utterance):
	words = [uncontract(word) for word in nltk.word_tokenize(utterance)]
	tagged_words = tagger.tag(words)
	return { 'tagged_words' : tagged_words }
