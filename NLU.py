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

# Remove contractions from word
# return word
def uncontract(word):
  if word in contractions:
    return contractions[word]
  return word

# Classify the dialog act of a sentence
# Replace named entities with object/class label to form meta-sentence
# Return act classification, along with any extra info
def classify_dialog_act(tagged_words, entities):
  return 'pref'
  
def NLU(data):
  # uncontract and tokenize utterance
  words = [uncontract(word) for word in nltk.word_tokenize(data['user_utterance'])]
  # tag words with saved tagger
  tagged_words = tagger.tag(words)
  # get any recognized entities
  entities = nerdb.get_entities(data['user_utterance'])
  # classify the dialog act
  act = classify_dialog_act(tagged_words, entities)
  data['tagged_words'] = tagged_words
  data['entities'] = entities
  data['act'] = act
  # add entity to pos and neg preference set
  data['pos'] = set()
  data['neg'] = set()
  data['prefs'] = {}
  for word in pos:
    if word in words:
      for (type_name, entity, s) in data['entities']:
        data['pos'].add((type_name, entity))
        data['prefs'][entity] = word
  for word in neg:
    if word in words:
      for entity in data['entities']:
        data['neg'].add(entity)
        data['prefs'][entity] = word
  schema = data['user_utterance']
  for (type_name, entity, s) in data['entities']:
    schema = schema.replace(s, type_name)
  data['utterance_schema'] = schema
