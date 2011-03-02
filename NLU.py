import nltk
import NERDb
from Ontology import *

contractions = {
  "'s" : 'is',
  "n't" : 'not',
  "'re" : 'are',
  "'m" : 'am',
}

nerdb = NERDb.NERDb()
prefs = [line.strip() for line in open('preferences.txt').readlines()]
pos = prefs[prefs.index("# pos")+1:prefs.index("# neg")]
neg = prefs[prefs.index("# neg")+1:]
trivias = [line.strip().split(', ') for line in open('trivia_types.txt').readlines()]

# Remove contractions from word
# return word
def uncontract(word):
  if word in contractions:
    return contractions[word]
  return word
  
def NLU(data):
<<<<<<< HEAD

=======
  # uncontract and tokenize utterance
  words = [uncontract(word) for word in nltk.word_tokenize(data['user_utterance'])]
  # tag words with saved tagger
  tagged_words = tagger.tag(words)
  # get any recognized entities
  entities = nerdb.get_entities(data['user_utterance'])
  data['tagged_words'] = tagged_words
  data['entities'] = map(lambda (type_name, id, s): (type_name, id), entities)
  # add entity to pos and neg preference set
  data['pos'] = set()
  data['neg'] = set()
  data['prefs'] = {}
  for word in pos:
    if word in words:
      for (type_name, entity, s) in data['entities']:
        data['pos'].add((type_name, entity))
        data['prefs'][entity] = word
        data['act'] = 'pref'
  for word in neg:
    if word in words:
      for entity in data['entities']:
        data['neg'].add(entity)
        data['prefs'][entity] = word
        data['act'] = 'pref'
  schema = data['user_utterance']
  for (type_name, entity, s) in entities:
    schema = schema.replace(s, type_name)
  data['schema'] = schema
  for schema, attr in trivias:
    if schema in data['schema']:
      data['act'] = 'trivia'
      data['trivias'] = [{}]
      data['trivias'][0]['attr'] = attr
      data['trivias'][0]['entities'] = data['entities']
>>>>>>> james/master
