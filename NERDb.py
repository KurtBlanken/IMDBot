import nltk
from nltk.corpus import conll2000, brown
import Levenshtein as lev
import cPickle
import re

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
    tagged_sent = nltk.pos_tag(re.split(r'[ \n!#$%&\*^()/?.]+', sentence))
    history = []
    for i, word in enumerate(tagged_sent):
      featureset = npchunk_features(tagged_sent, i, history)
      tag = self.classifier.classify(featureset)
      history.append(tag)
    chunked_sent = zip(tagged_sent, history)
    conlltags = [(w,t,c) for ((w,t),c) in chunked_sent]
    return nltk.chunk.conlltags2tree(conlltags)

class NERDb():
	def __init__(self):
		try:
			tagger = cPickle.load(open('pickles/nerdb_tagger.pkl'))
		except IOError:
			print 'failed to load nerdb_tagger, recreating...'
			train_sents = conll2000.tagged_sents() + brown.tagged_sents()
			tagger = nltk.DefaultTagger('NN')
			tagger = nltk.UnigramTagger(train_sents, backoff=tagger)
			tagger = nltk.BigramTagger(train_sents, backoff=tagger)
			tagger = nltk.TrigramTagger(train_sents, backoff=tagger)
			cPickle.dump(tagger, open('pickles/nerdb_tagger.pkl', 'w'))
			print 'done'
		try:
			chunker = cPickle.load(open('pickles/nerdb_chunker.pkl'))
		except IOError:
			print 'failed to load nerdb_chunker, recreating...'
			train_sents = conll2000.chunked_sents()
			chunker = ConsecutiveNPChunker(tagger, train_sents)
			cPickle.dump(chunker, open('pickles/nerdb_chunker.pkl', 'w'))
			print 'done'
		self.chunker = chunker
		self.people = [line.strip().split(" ", 1) for line in open('data/actors_index.txt').readlines()]
		self.people += [line.strip().split(" ", 1) for line in open('data/actresses_index.txt').readlines()]
		self.people += [line.strip().split(" ", 1) for line in open('data/other_people.txt').readlines()]
		for i, (id, person) in enumerate(self.people):
			names = person.split(',')
			names = map(lambda name: name.strip(), names)
			names.reverse()
			name = ' '.join(names).lower()
			self.people[i] = (long(id), name)
		self.movies = [line.strip().split(" ", 1) for line in open('data/title_index.txt').readlines()]
		self.movies = map(lambda (id, movie): (long(id), movie.lower()), self.movies)
		self.genres = [line.strip().split(" ", 1) for line in open('data/genres.txt').readlines()]
		self.entity_types = {'PERSON' : self.people, 'MOVIE' : self.movies, 'GENRE' : self.genres}
		self.numbers = eval(open('data/numbers.txt').read())
		 
	def search(self, s, t):
		for type_name, entities in self.entity_types.items():
			matches = find_matches(s.lower(), type_name, entities, t)
			if len(matches) > 0:
				return matches[0][1]
		return None

	def get_entities(self, sentence):
		found = set()
		sent_list= []
		sent_list.append(sentence)
		# check for numbers to check if there are matches
		words= re.split(r'[ \n!#$%&\*^()/.?]+',sentence)
		for word in words:
			if word.isdigit():
				if word in self.numbers:
					replaced = sentence.replace(word, self.numbers[word].title())
					sent_list.append(replaced) 			
		for sentence in sent_list:
		 	tree = self.chunker.parse(sentence)
		 	for child in tree.subtrees():
		 		if child.node == 'NP':
		 			match = self.search(' '.join(map(lambda x: x[0], child.leaves())), 0.99)
		 			if match:
		 				found.add(match)
		 	tokens = re.split(r'[ \n!#$%&\*^()/.?]+',sentence)
		 	for i in range(len(tokens)):
		 		for j in range(len(tokens)):
		 			if i+j+1 < len(tokens):
		 				substring = ' '.join(tokens[i:i+j+1])
		 				match = self.search(substring, 0.99)
		 				if match:
		 					found.add(match)
		# remove any entities that are substrings of another entity
		dupes = set()
		for entity1 in found:
			for entity2 in found:
				if entity1 not in dupes and entity2 not in dupes:
					t1, id1, name1 = entity1
					t2, id2, name2 = entity2
					if id1 != id2:
						names1 = name1.split()
						names2 = name2.split()
						d = []
						for n1 in names1:
							for n2 in names2:
								d.append(lev.ratio(n1, n2))
						if max(d) > 0.8 and t1 != 'GENRE':
							if len(name2) > len(name1):
								dupes.add(entity1)
							else:
								dupes.add(entity2)
		return found.difference(dupes)

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

def find_matches(s, type_name, entities, t):
  matches = []
  for id, entity in entities:
    r = lev.ratio(s, entity)
    if r > t:
      matches.append((r, (type_name, id, entity)))
  matches.sort(key=lambda x: x[1], reverse=True)
  return matches

def test():
  import random
  nerdb = NERDb()
  entity_types = {}
  for type_name, entities in nerdb.entity_types.items():
    entity_types[type_name] = map(lambda (id, name): (id, name.strip()), entities)
  schemas = [
    "What movies have PERSON and PERSON been in together?",
    "PERSON is funny.",
    "What about something with PERSON?",
    "Who is PERSON?",
    "I hate PERSON",
    "Was PERSON in MOVIE?",
    "What's the plot of MOVIE?",
    "I like GENRE films",
    "How many GENRE movies has PERSON been in?",
  ]

  def is_printable_name(name):
    for c in name:
      if ord(c) > 127:
        return False
    return True

  def gen_random_sentence(schema):
    sentence = schema
    inserts = []
    for type_name, entities in entity_types.items():
      for i in range(sentence.count(type_name)):
        entity = random.choice(entities)
        while not is_printable_name(entity[1]):
          entity = random.choice(entities)
        inserts.append(entity)
        sentence = sentence.replace(type_name, entity[1], 1)
    return sentence, inserts
  
  err = 0
  fperr = 0
  count = 0
  samples = 10
  import time
  start = time.time()
  for schema in schemas:
    for i in range(samples):
      sentence, entities = gen_random_sentence(schema)
      entities_ids = [entity[0] for entity in entities]
      found = nerdb.get_entities(sentence)
      found_ids = [entity[1] for entity in found]
      num_found = sum([1 for entity in entities_ids if entity in found_ids])
      false_positives = sum([1 for entity in found_ids if entity not in entities_ids])
      err += len(entities) - num_found
      fperr += false_positives
      count += len(entities)
  end = time.time()
  sentences = samples * len(schemas)
  print 'ned results for {0} schemas, {1} sentences total, {2:.2f} seconds/result'.format(
    len(schemas), sentences, (end-start)/sentences)
  print '{0} missed from {1} possible ({2:.0f}%)'.format(err, count, (err/float(count))*100)
  print '{0} sentences with false positives ({1:.0f}%)'.format(fperr, (fperr/float(sentences))*100)

if __name__ == '__main__':
	test()

'''
Ablation Study Results (PERSON and MOVIE types only):
  Baseline (everything on):
    ned results for 7 schemas, 700 sentences total, 0.75 seconds/result
    6 missed from 900 possible (1%)
    53 sentences with false positives (8%)
  Max sub-token length len(tokens)/2:
    ned results for 7 schemas, 700 sentences total, 0.48 seconds/result
    39 missed from 900 possible (4%)
    55 sentences with false positives (8%)
  Chunk matching only:
    ned results for 7 schemas, 700 sentences total, 0.05 seconds/result
    327 missed from 900 possible (36%)
    51 sentences with false positives (7%)
  Sub-tokens only:
    ned results for 7 schemas, 700 sentences total, 0.72 seconds/result
    101 missed from 900 possible (11%)
    21 sentences with false positives (3%)
'''
