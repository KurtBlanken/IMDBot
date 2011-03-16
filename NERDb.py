import os
import nltk
import Levenshtein as lev
import re
import imdbi
import cPickle
import stanford_parser

class NERDb():

	def __init__(self):
		a = imdbi.IMDBInterface()
		if not os.path.exists('pickles/people_cache.pkl'):
			people = a.get_persons()
			people_cache = {}
			for id, name in people:
				if ', ' not in name:
					print name
					continue
				last, first = name.split(', ')
				last = last.lower()
				first = first.lower()
				if first not in people_cache:
					people_cache[first] = {}
				people_cache[first][last] = id
			cPickle.dump(people_cache, open('pickles/people_cache.pkl', 'w'))
		else:
			people_cache = cPickle.load(open('pickles/people_cache.pkl'))
		self.a = a
		self.people_cache = people_cache
		self.genres = {}
		for genre, keyword in [line.strip().split() for line in open('data/genres.txt').readlines()]:
			self.genres[keyword] = genre
		prefs = [line.strip() for line in open('data/preferences.txt').readlines() if len(line.strip()) > 0]
		self.pos_words = set(prefs[prefs.index("# pos")+1:prefs.index("# neg")])
		self.neg_words = set(prefs[prefs.index("# neg")+1:])
		self.parser = stanford_parser.StanfordParser()
		
	def search_person(self, first, last):
		first = first.lower()
		last = last.lower()
		if first in self.people_cache:
			firsts = self.people_cache[first]
			if last in firsts:
				return self.people_cache[first][last]
			else:
				ratios = []
				for _last in firsts.keys():
					r = lev.ratio(str(last), str(_last))
					ratios.append((r, firsts[_last]))
				ratios.sort(key=lambda x: x[0], reverse=True)
				return ratios[0][1]
		return None
		
	def search_movie(self, keywords):
		self.a.cur.execute("SELECT id, title FROM title WHERE title LIKE '%{0}%'".format('%'.join(keywords)))
		matches = []
		for (id, match) in self.a.cur.fetchall():
			matches.append((lev.ratio(str(' '.join(keywords)), str(match)), id, match))
		matches.sort(key=lambda x: x[0], reverse=True)
		if matches:
			return matches[0][1]
		return None
		
	def search_genres(self, keywords):
		genres = []
		for keyword in keywords:
			if keyword in self.genres:
				genres.append(self.genres[keyword])
		return genres

	def get_entities_and_prefs(self, sentence):
		tree, deps = self.parser.parse(sentence)
		entities = []
		for subtree in tree.subtrees(filter=lambda tree: tree.node == 'NP'):
			if list(subtree.subtrees(filter=lambda tree: tree.node == 'PRP')):
				continue
			keywords = subtree.leaves()
			key_string = ' '.join(keywords)
			matches = []
			if len(keywords) == 2:
				person = self.search_person(keywords[0], keywords[1])
				if person:
					matches.append(('PERSON', person))
			movie = self.search_movie(keywords)
			if movie:
				matches.append(('MOVIE', movie))
			genres = self.search_genres(keywords)
			if genres:
				entities += [('GENRE', genre, key_string) for genre in genres]
			for t, id in matches:
				r = 1.0
				if t == 'PERSON':
					name = self.a.get_person(id, cast_info=False)['name']
					r = lev.ratio(str(key_string), str(name))
				elif t == 'MOVIE':
					title = self.a.get_movie(id, aka_info=False, movie_info=False, cast_info=False)['title']
					r = lev.ratio(str(key_string), str(title))
				if r > 0.9:
					entities.append((t, id, key_string))
		#todo: remove false-positive entities, check for quoted entity names
		pos = set()
		neg = set()
		for dep_type, parent, i1, child, i2 in deps:
			if parent in self.pos_words:
				pass
			elif parent in self.neg_words:
				pass
		return entities, pos, neg

'''
def schema_test():
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
'''
  
def test():
   db = NERDb()
   print 'Welcome to the IMDBot NERDb'
   while 1:
   	try:
   		s = raw_input("> ")
   		print db.get_entities_and_deps(s)
   	except EOFError:
   		sys.exit(0)

if __name__ == '__main__':
	import sys
	test()
