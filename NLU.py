import nltk
import NERDb, DM
from Ontology import *

contractions = {
  "'s" : 'is',
  "n't" : 'not',
  "'re" : 'are',
  "'m" : 'am',
}

nerdb = NERDb.NERDb()

porter= nltk.PorterStemmer()

prefs = [line.strip() for line in open('data/preferences.txt').readlines() if len(line.strip()) > 0]
pos = set(prefs[prefs.index("# pos")+1:prefs.index("# neg")])
neg = set(prefs[prefs.index("# neg")+1:])
trivias = [line.strip().split(', ') for line in open('data/trivia_types.txt').readlines()]
numbers = eval(open('data/numbers.txt').read())


# Remove contractions from word
# return word
def uncontract(word):
  if word in contractions:
    return contractions[word]
  return word
  
def NLU(data):
  # uncontract and tokenize utterance
  '''
  Input: {'errors': [], 'prefs': set([]), 'imdbi': <imdbi.IMDBInterface object at 0x10a334350>, 'id': 'console', 'user_utterance': 'Who directed Armageddon?'}
  '''
  words = [uncontract(word) for word in nltk.word_tokenize(data['user_utterance'])]
  # tag words with saved tagger
  tagged_words = nltk.pos_tag(nltk.word_tokenize(data['user_utterance']))
  entitites= set()
  sentence= data['user_utterance']
  
  #print sentence
  # get any recognized entities
  entities = nerdb.get_entities(sentence)
  #print entities
  data['tagged_words'] = tagged_words
  data['entities'] = map(lambda (type_name, id, s): (type_name, id), entities)
  #print entities
  #print data['entities']
  
  # add entity to pos and neg preference set
  data['pos'] = set()
  data['neg'] = set()
  data['prefs'] = {}
  data['act']=''
  
  tagged= nltk.pos_tag(nltk.word_tokenize(sentence))
  
  for (word, tag) in tagged:
  	if tag.find('VB') != -1 or tag == 'JJ':
  		stem= porter.stem(word)
  		if stem in pos or word in pos:
  			for (type_name, entity) in data['entities']:
  				data['pos'].add((type_name, entity))
  				data['prefs'][entity] = word
  				data['act']= 'pref'
  		elif stem in neg or word in neg:
  			for (type_name, entity) in data['entities']:
  				data['neg'].add((type_name, entity))
  				data['prefs'][entity] = word
  				data['act']= 'pref'
  
  '''
  for word in pos:
    if word in words:
      for (type_name, entity) in data['entities']:
        data['pos'].add((type_name, entity))
        data['prefs'][entity] = word
        data['act'] = 'pref'
  for word in neg:
    if word in words:
      for entity in data['entities']:
        data['neg'].add(entity)
        data['prefs'][entity] = word
        data['act'] = 'pref'
        '''
  
  schema = sentence
  for (type_name, entity, s) in entities:
    schema = schema.replace(s, type_name)
  data['schema'] = schema
  for schema, attr in trivias:
  	if schema in data['schema']:
  		data['act'] = 'trivia'
  		data['trivia'] = {}
  		data['trivia']['attr'] = attr
  		data['trivia']['entities'] = data['entities']
  		
  
  # pass data into DM
  #print data
  DM.DM(data)
      
