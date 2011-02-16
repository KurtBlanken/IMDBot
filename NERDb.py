import nltk
import Levenshtein as lev

''' Levenshtein examples:
jaro(string1, string2)

    The Jaro string similarity metric is intended for short strings like
    personal last names.  It is 0 for completely different strings and
    1 for identical strings.
    
ratio(string1, string2)
    
    The similarity is a number between 0 and 1, it's usually equal or
    somewhat higher than difflib.SequenceMatcher.ratio(), because it's
    based on real minimal edit distance.
'''
	
sentences = [
	"What movies have Bill Murray and Danny DeVito been in together?",
	# current ne chunker fails to recognize Danny DeVito as a single person,
	# gets Danny, but not DeVito.
	"Danny DeVito is funny.",
	#"I like racing car movies like Gone in 60 Seconds.",
	"What about something with Nicole Kidman?",
]

'''
	nltk has a default Named Entity chunker!!
	why didn't we know about this before!?
'''
def extract_entities(sentence):
	entities = {
		'people' : []
	}
	for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence))):
		if hasattr(chunk, 'node') and chunk.node == 'PERSON':
			entities['people'].append(' '.join(c[0] for c in chunk.leaves()))
	return entities

def pairs(lst):
	i = iter(lst)
	first = prev = i.next()
	for item in i:
		yield prev, item
		prev = item
	yield item, first

actors = [line.split(" ", 1) for line in open('actors_index.txt').readlines()]
for sentence in sentences:
	matches = {}
	for person in extract_entities(sentence)['people']:
		ratios = []
		for id, actor in actors:
			s = actor.strip().replace(' ', '').split(',')
			if len(s) == 1:
				actor = s[0]
			else:
				actor = s[1] + ' ' + s[0]
			r = lev.jaro(person, actor)
			if r > 0.9:
				ratios.append((r, id, actor))
		ratios.sort(key=lambda x: x[0], reverse=True)
		if len(ratios) > 0:
			r, id, actor = ratios[0]
			matches[person] = { 'id' : id, 'name' : actor, 'class' : 'actor' }
	for match in matches:
		print sentence.replace(match, '(' + matches[match]['class'] + ' ' + matches[match]['id'] + ')')
