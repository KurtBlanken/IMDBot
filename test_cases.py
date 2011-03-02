cases = [
(
# utterance
'When was Armageddon made?',
# NLU output / dialog manager input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'when',
      'entity' : ('movie', 48368),
    }]
},
# dialog manager output / NLG input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'when',
      'entity' : ('movie', 48368),
      'answer' : 1998,
    }]
},
[
  '1998.',
  'The production year was 1998.',
]
),

(
# utterance
'Was Matt Damon in Armageddon?',
# NLU output / dialog manager input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'in',
      'entities' : [('person', 260886), ('movie', 48368)],
    }]
},
# dialog manager output / NLG input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'in',
      'entities' : [('person', 260886), ('movie', 48368)],
      'answer' : False,
    }]
},
[
  'No.',
  "I don't think so.",
]
),

(
# utterance
'Was Ben Affleck in Armageddon?',
# NLU output / dialog manager input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'in',
      'entities' : [('person', 8590), ('movie', 48368)],
    }]
},
# dialog manager output / NLG input
{  'act' : 'trivia',
  'trivias' : [
    {  'attr' : 'in',
      'entities' : [('person', 260886), ('movie', 48368)],
      'answer' : False,
    }]
},
[
  'No.',
  "I don't think so.",
]
),

(
# utterance
'I think Danny Devito is hilarious',
# NLU output / dialog manager input
{  'act' : 'pref',
  'pos' : set([('actor', 291778)]),
  'neg' : set(),
},
# dialog manager output / NLG input
{  'act' : 'pref',
  'pos' : set([('actor', 291778)]),
  'neg' : set(),
  'prefs' : { ('actor', 291778) : 'hilarious' }
},
[
  'Ok.',
  'I agree.',
]
),

(
# utterance
'I think Fubie Fubar is hilarious',
# NLU output / dialog manager input
{  'act' : 'pref',
  'pos' : set(),
  'neg' : set(),
},
# dialog manager output / NLG input
{  'act' : 'pref',
  'pos' : set(),
  'neg' : set(),
  'prefs' : {},
},
[
  "I don't understand.",
  "I don't know about Fubie Fubar.",
  "Huh?",
]
),
] # end cases

## PYTHON CODE ##
import NLU, DM, NLG
from imdbi import IMDBInterface
imdbi = IMDBInterface()
lines = open('test_cases.py').readlines()
end = 0
for i, line in enumerate(lines):
  if '## PYTHON CODE ##' in line:
    end = i-1
    break
lines = filter(line.strip, lines[:end])
d = {}
exec ''.join(lines) in d
for utterance, nlu_dm, dm_nlg, outputs in d['cases']:
  nlu_dm['imdbi'] = imdbi
  nlu_dm['id'] = 'test'
  nlu_dm['errors'] = []
  dm_nlg['imdbi'] = imdbi
  dm_nlg['id'] = 'test'
  dm_nlg['errors'] = []
  print '> ' + utterance
  
  data = {
    'id' : 'test',
    'user_utterance' : utterance,
    'pos' : set(),
    'neg' : set(),
    'prefs' : {},
    'errors' : [],
    'imdbi' : imdbi,
  }
  try:
    NLU.NLU(data)
  except:
    print 'NLU failed on', utterance
  else:
    print 'NLU:'
    print data
  try:
    DM.DM(nlu_dm)
  except:
    print 'DM failed on', utterance
  else:
    print 'DM'
    print nlu_dm
  try:
    NLG.NLG(dm_nlg)
  except:
    print 'NLG failed on', utterance
  else:
    print 'NLG'
    print dm_nlg
