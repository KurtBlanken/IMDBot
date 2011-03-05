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
    #tagged_sent = self.tagger.tag(nltk.word_tokenize(sentence))
    #tagged_sent = nltk.pos_tag(nltk.word_tokenize(sentence))
    tagged_sent= nltk.pos_tag(re.split(r'[ \n!#$%&\*^()/]+',sentence))
    #tagged_sent= nltk.pos_tag(nltk.word_tokenize(sentence.replace("'", '').replace(',', '')))
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
      tagger = cPickle.load(open('nerdb_tagger.pkl'))
    except IOError:
      print 'failed to load nerdb_tagger, recreating...'
      train_sents = conll2000.tagged_sents() + brown.tagged_sents()
      tagger = nltk.DefaultTagger('NN')
      tagger = nltk.UnigramTagger(train_sents, backoff=tagger)
      tagger = nltk.BigramTagger(train_sents, backoff=tagger)
      tagger = nltk.TrigramTagger(train_sents, backoff=tagger)
      cPickle.dump(tagger, open('nerdb_tagger.pkl', 'w'))
      print 'done'
    try:
      chunker = cPickle.load(open('nerdb_chunker.pkl'))
    except IOError:
      print 'failed to load nerdb_chunker, recreating...'
      train_sents = conll2000.chunked_sents()
      chunker = ConsecutiveNPChunker(tagger, train_sents)
      cPickle.dump(chunker, open('nerdb_chunker.pkl', 'w'))
      print 'done'
    self.chunker = chunker
    self.people = [line.strip().split(" ", 1) for line in open('actors_index.txt').readlines()]
    self.people += [line.strip().split(" ", 1) for line in open('actresses_index.txt').readlines()]
    self.movies = [line.strip().split(" ", 1) for line in open('title_index.txt').readlines()]
    self.entity_types = {'PERSON' : self.people, 'MOVIE' : self.movies}
    
  def search(self, s, t):
    for type_name, entities in self.entity_types.items():
      matches = find_matches(s, type_name, entities, t)
      if len(matches) > 0:
        return matches[0][1]
    return None

  def get_entities(self, sentence):
    found = set()
    tree = self.chunker.parse(sentence)
    #print tree
    for child in tree.subtrees():
      if child.node == 'NP':
        match = self.search(' '.join(map(lambda x: x[0], child.leaves())), 0.9)
        if match:
          found.add(match)
    #tokens = nltk.word_tokenize(sentence.replace("'", '').replace(',', ''))
    tokens = re.split(r'[ \n!#$%&\*^()/]+',sentence)
    #print tokens
    for i in range(len(tokens)):
      for j in range(1,len(tokens)):
        if i+j+1 < len(tokens):
          substring = ' '.join(tokens[i:i+j+1])
          match = self.search(substring, 0.99)
          if match:
            found.add(match)
    return found

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

def find_matches(s, type_name, entities, movies, t=0.9):
  matches = []
  for id, entity in entities:
    if type_name == 'PERSON':
      entity = entity.split(',')
      # strip whitespace from entity elements
      for (i, el) in enumerate(entity):
      	entity[i]= el.strip()
      entity.reverse()
      entity = ' '.join(entity)
    r = lev.ratio(s.lower(), entity.lower())
    if r > t:
      matches.append((r, (type_name.lower(), long(id), entity))) # db returns ids as longs
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
        while not is_printable_name(entity[1]) or len(entity[1].split(',')) == 1:
          entity = random.choice(entities)
        inserts.append(entity)
        if type_name == 'PERSON':
          last, first = entity[1].split(',')
          sentence = sentence.replace(type_name, first.strip() + ' ' + last.strip(), 1)
        else:
          sentence = sentence.replace(type_name, entity[1])
    return sentence, inserts
  
  err = 0
  fperr = 0
  count = 0
  samples = 100
  import time
  start = time.time()
  for schema in schemas:
    for i in range(samples):
      sentence, entities = gen_random_sentence(schema)
      found = nerdb.get_entities(sentence)
      err += len(entities) - sum([1 for entity in entities if entity in found])
      if [entity for entity in found if entity not in entities]:
        fperr += 1
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
Ablation Study Results:
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
