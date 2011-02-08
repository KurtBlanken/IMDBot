act_types = ['pref', 'trivia', 'chat', 'info', 'rec']
entity_types = ['genre', 'person', 'movie']
genre_types = [
	'comedy', 'action', 'adventure', 'animation', 'biography', 'crime',
	'documentary', 'drama', 'family', 'fantasy', 'noir', 'horror',
]
relationship_types = ['in', 'attrib']

import cPickle
# Saved tagger
tagger_file = open('tagger.pkl', 'rb')
tagger = cPickle.load(tagger_file)
tagger_file.close()

from nltk.corpus import wordnet
# attempt to map from word to entity_type
def find_entity(word, tag, tagged_words):
	# see if word matches any of the genres in genre_types
	if len(wordnet.synsets(word)) == 0:
		return None
	for s in wordnet.synsets(word):
		for t in genre_types:
			for	s1 in wordnet.synsets(t):
				if s1 == s:
					return ('genre', t)
	# check if word matches a person
	# check if word matches a movie
