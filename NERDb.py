import nltk, re
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

def insert(s, i, d):
	if s[0] not in d:
		d[s[0]] = ([], {})
	if len(s) == 1:
		d[s[0]][0].append(i)
	else:
		insert(s[1:], i, d[s[0]][1])

titles = [line.strip().split(' ', 1)
						for line in open('title_index.txt').readlines()]
d = {}
for id, title in titles:
	insert(title, id, d)

def lookup(s, d):
	if len(s) == 1:
		return d[s][0]
	return lookup(s[1:], d[s[0]][1])

def query(s):
	results = []
	for id, title in titles:
		l = lev.ratio(s, title)
		results.append((l, id, title))
	results.sort(key=lambda r: r[0], reverse=True)
	return results

def pairs(lst):
	i = iter(lst)
	first = prev = i.next()
	for item in i:
		yield prev, item
		prev = item
	yield item, first

"""
This classed must be passed in the train set

class UnigramChunker(nltk.chunk.ChunkParserI):
	def __init__(self, train_sents):
		train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
									for sent in train_sents]
		self.tagger = nltk.UnigramTagger(train_data)
	def parse(self, sentence):
		pos_tags = [pos for (word, pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)
		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		conlltags = [(word, pos, chunktag) for ((word, pos), chunktag) in zip(sentence, chunktags)]
		return nltk.chunk.conlltags2tree(conlltags)

class UnigramChunker(nltk.chunk.ChunkParserI):
	def __init__(self):
		train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
									for sent in nltk.corpus.conll2000.chunked_sents()]
		self.tagger = nltk.UnigramTagger(train_data)
	def parse(self, sentence):
		pos_tags = [pos for (word, pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)
		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		conlltags = [(word, pos, chunktag) for ((word, pos), chunktag) in zip(sentence, chunktags)]
		return nltk.chunk.conlltags2tree(conlltags)
"""
def getEntities(sentence):
	
	print sentence
	
	try:
		import cPickle as pickle
	except:
		import pickle
	
	fh= open('eChunker.pkl','r')
	chunker = pickle.load(fh)
	fh.close()
		
		
	patterns = [(r'[A-Z][a-z]+','NNP'),]
	regexp_tagger= nltk.RegexpTagger(patterns)
	tagger = nltk.UnigramTagger(nltk.corpus.treebank.tagged_sents(), backoff=regexp_tagger )
		
	actors = [line.split(" ", 1) for line in open('actors_index.txt').readlines()]
		
	tagged_sent = tagger.tag(nltk.word_tokenize(sentence))
	tree = chunker.parse(tagged_sent)
		
		
		
	""" Entities is a list of lists to facilitate pairing
	 	  with multiple entities in a sentence
	"""
	entities=[]
	for subtree in tree.subtrees():
		# get NP chunks
		if subtree.node == 'NP':
			nplist=[]
			# check if NP contains any NNP 
			for child in subtree:
				name,tag= child
				if tag == 'NNP': nplist.append(name)
			
			if len(nplist) > 0: entities.append(nplist)
	
	print entities
		
	matches= {}
	for list in entities:
		for pair in pairs(list):
			first, last= pair
			name= first + ' ' + last
			print name
			ratios = []
			for id, actor in actors:
				s= actor.strip().replace(' ', '').split(',')
				if len(s) == 1:
					actor= s[0]
				else:
					actor = s[1] + ' ' + s[0]
				ratio= lev.jaro(name,actor)
				if ratio >= 0.9:
					ratios.append((ratio,id,actor))
			ratios.sort(key=lambda x: x[0], reverse= True)
			if len(ratios) > 0:
				r, id, actor = ratios[0]
				matches[pair] = {'id':id, 'name': actor, 'class': 'actor'}
	return matches

"""
try:
	import cPickle as pickle
except:
	import pickle
	
fh= open('eChunker.pkl','r')
chunker = pickle.load(fh)
fh.close()
patterns = [(r'[A-Z][a-z]+','NNP'),]
regexp_tagger= nltk.RegexpTagger(patterns)
tagger = nltk.UnigramTagger(nltk.corpus.treebank.tagged_sents(), backoff=regexp_tagger )
	
sentences = [
	"What movies have Bill Murray and Danny DeVito been in together?",
	"Danny DeVito is funny.",
	#"I like racing car movies like Gone in 60 Seconds.",
	"What about something with Nicole Kidman?",
	"Where is James Cameron?",
	"I hate Sylvester Stallone",

]



actors = [line.split(" ", 1) for line in open('actors_index.txt').readlines()]

#actors = [re.split(r' ', line) for line in open('actors_index.txt').readlines()]



for sentence in sentences:
	tagged_sent = tagger.tag(nltk.word_tokenize(sentence))
	tree = chunker.parse(tagged_sent)

	 Entities is a list of lists to facilitate pairing
	    with multiple entities in a sentence
	
	entities=[]
	for subtree in tree.subtrees():
		# get NP chunks
		if subtree.node == 'NP':
			nplist=[]
			# check if NP contains any NNP 
			for child in subtree:
				name,tag= child
				if tag == 'NNP': nplist.append(name)
			
			if len(nplist) > 0: entities.append(nplist)
	
	print entities
	
	#pairing= [pair for pair in pairs(entities)]
	#print pairing
	
	matches= {}
	for list in entities:
		for pair in pairs(list):
			first, last= pair
			name= first + ' ' + last
			print name
			ratios = []
			for id, actor in actors:
				s= actor.strip().replace(' ', '').split(',')
				if len(s) == 1:
					actor= s[0]
				else:
					actor = s[1] + ' ' + s[0]
				ratio= lev.jaro(name,actor)
				if ratio >= 0.9:
					ratios.append((ratio,id,actor))
			ratios.sort(key=lambda x: x[0], reverse= True)
			if len(ratios) > 0:
				r, id, actor = ratios[0]
				matches[pair] = {'id':id, 'name': actor, 'class': 'actor'}
				
	for match in matches:
		first, last = match
		name = first + ' ' + last
		print sentence.replace(name, '(' + matches[match]['class'] + ' ' + matches[match]['id'] + ')')
"""
	
"""				
	# this is the same as tagged_sent
	nnps = [word for (word, tag) in tree.leaves() if tag in ['NNP', None]]
	matches = {}
	for pair in pairs(nnps):
		first, last = pair
		name = first + ' ' + last
		ratios = []
		for id, actor in actors:
			s = actor.strip().replace(' ', '').split(',')
			if len(s) == 1:
				actor = s[0]
			else:
				actor = s[1] + ' ' + s[0]
			r = lev.jaro(name, actor)
			if r > 0.8:
				ratios.append((r, id, actor))
		ratios.sort(key=lambda x: x[0], reverse=True)
		if len(ratios) > 0:
			r, id, actor = ratios[0]
			matches[pair] = { 'id' : id, 'name' : actor, 'class' : 'actor' }
	for match in matches:
		first, last = match
		name = first + ' ' + last
		print sentence.replace(name, '(' + matches[match]['class'] + ' ' + matches[match]['id'] + ')')
"""