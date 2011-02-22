import nltk
import Levenshtein as lev

class ConsecutiveNPChunker(nltk.ChunkParserI):
	def __init__(self, tagger, chunked_sents):
		tagged_sents = [[((w,t),c) for (w, t, c) in
										 nltk.chunk.tree2conlltags(sent)]
										for sent in chunked_sents]								
		train_set = []
		for tagged_sent in tagged_sents:
			untagged_sent = nltk.tag.untag(tagged_sent)
			history = []
			for i, (word, tag) in enumerate(tagged_sent):
				featureset = npchunk_features(untagged_sent, i, history)
				train_set.append((featureset, tag))
				history.append(tag)
		labels = set(label for (tok,label) in train_set)
		nltk.config_megam('./megam_i686.opt')
		self.classifier = nltk.MaxentClassifier.train(train_set, algorithm='megam')
		self.tagger = tagger
		
	def parse(self, sentence):
		tagged_sent = self.tagger.tag(nltk.word_tokenize(sentence))
		history = []
		for i, word in enumerate(tagged_sent):
			featureset = npchunk_features(tagged_sent, i, history)
			tag = self.classifier.classify(featureset)
			history.append(tag)
		chunked_sent = zip(tagged_sent, history)
		conlltags = [(w,t,c) for ((w,t),c) in chunked_sent]
		return nltk.chunk.conlltags2tree(conlltags)

def tags_since_dt(sentence, i):
	tags = set()
	for word, pos in sentence[:i]:
		if pos == 'DT':
			tags = set()
		else:
			tags.add(pos)
	return '+'.join(sorted(tags))
	
def npchunk_features(sentence, i, history):
	word, pos = sentence[i]
	if i == 0:
		prevword, prevpos = "<START>", "<START>"
	else:
		prevword, prevpos = sentence[i-1]
	if i == len(sentence)-1:
		nextword, nextpos = "<END>", "<END>"
	else:
		nextword, nextpos = sentence[i+1]
	return {
		'pos' : pos,
		'word' : word,
		'prevword' : prevword,
		'prevpos' : prevpos,
		'nextpos' : nextpos,
		'nextword' : nextword,
		'tags-since-dt' : tags_since_dt(sentence, i),
	}
	
def find_matches(names, people):
	matches = []
	for id, person in people:
		names2 = person.split(',')
		names2.reverse()
		r = sum([lev.jaro(n1, n2) for n1, n2 in zip(names, names2)]) / len(zip(names, names2))
		if r > 0.75:
			matches.append((r, (id, person)))
	matches.sort(key=lambda x: x[0], reverse=True)
	return matches

def test():
	import random
	people = [line.split(" ", 1) for line in open('actors_index.txt').readlines()]
	people += [line.split(" ", 1) for line in open('actresses_index.txt').readlines()]
	people = map(lambda (id, name): (id, name.strip()), people)
	schemas = [
		"What movies have PERSON and PERSON been in together?",
		"PERSON is funny.",
		"What about something with PERSON?",
		"Who is PERSON?",
		"I hate PERSON",
		"Was PERSON in MOVIE",
	]

	def is_printable_name(name):
		for c in name:
			if ord(c) > 127:
				return False
		return True

	def gen_random_sentence(schema):
		sentence = schema
		for i in range(sentence.count('PERSON')):
			name = random.choice(people)[1]
			while not is_printable_name(name) or len(name.split(',')) == 1:
				name = random.choice(people)[1]
			last, first = name.split(',')
			sentence = sentence.replace('PERSON', first.strip() + ' ' + last.strip(), 1)
		return sentence

	import cPickle
	from nltk.corpus import conll2000, brown
	try:
		tagger = cPickle.load(open('nerdb_tagger.pkl'))
	except IOError:
		train_sents = conll2000.tagged_sents()
		tagger = nltk.DefaultTagger('NN')
		tagger = nltk.UnigramTagger(train_sents, backoff=tagger)
		tagger = nltk.BigramTagger(train_sents, backoff=tagger)
		tagger = nltk.TrigramTagger(train_sents, backoff=tagger)
		cPickle.dump(tagger, open('nerdb_tagger.pkl', 'w'))
	try:
		chunker = cPickle.load(open('nerdb_chunker.pkl'))
	except IOError:
		train_sents = conll2000.chunked_sents()
		chunker = ConsecutiveNPChunker(tagger, train_sents)
		cPickle.dump(chunker, open('nerdb_chunker.pkl', 'w'))
	people = [line.strip().split(" ", 1) for line in open('actors_index.txt').readlines()]
	people += [line.strip().split(" ", 1) for line in open('actresses_index.txt').readlines()]
	for schema in schemas:
		sentence = gen_random_sentence(schema)
		print sentence
		tree = chunker.parse(sentence)
		entities = []
		for child in tree.subtrees():
			if child.node == 'NP' and (len(child.leaves()) == 2 or len(child.leaves()) == 3):
				matches = find_matches(map(lambda x: x[0], child.leaves()), people)
				if len(matches) > 0:
					entities.append(matches[0][1])
		if len(entities) == 0:
			tree.draw()
		print entities

if __name__ == '__main__':
	test()
