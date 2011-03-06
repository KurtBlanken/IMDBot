cases = [
(
# utterance
'When was Armageddon made?',
# NLU output / dialog manager input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'when',
  },
  'entities' : [('movie', 48368)],
},
# dialog manager output / NLG input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'when',
     'answer' : 1998,
  },
  'entities' : [('movie', 48368)],
},
[
  '1998',
  'The production year was 1998.',
]
),

(
# utterance
'Was Matt Damon in Armageddon?',
# NLU output / dialog manager input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'in',
  },
  'entities' : [('person', 260886), ('movie', 48368)],
},
# dialog manager output / NLG input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'in',
    'answer' : False,
  },
  'entities' : [('person', 260886), ('movie', 48368)],
},
[
  'No.',
]
),

(
# utterance
'Was Ben Affleck in Armageddon?',
# NLU output / dialog manager input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'in',
  },
  'entities' : [('person', 8590), ('movie', 48368)],
},
# dialog manager output / NLG input
{ 'act' : 'trivia',
  'trivia' : {
    'attr' : 'in',
    'answer' : True,
  },
  'entities' : [('person', 260886), ('movie', 48368)],
},
[
  'Yes.',
]
),

(
# utterance
'I think Danny Devito is hilarious',
# NLU output / dialog manager input
{ 'act' : 'pref',
  'pos' : set([('actor', 291778)]),
  'neg' : set(),
},
# dialog manager output / NLG input
{ 'act' : 'pref',
  'pos' : set([('actor', 291778)]),
  'neg' : set(),
  'prefs' : { ('actor', 291778) : 'hilarious' }
},
[
  'Yeah, Danny Devito is hilarious.',
  'I agree.',
  'Ok.',
]
),

(
# utterance
'I think Fubie Fubar is hilarious',
# NLU output / dialog manager input
{ 'act' : 'pref',
  'pos' : set(),
  'neg' : set(),
},
# dialog manager output / NLG input
{ 'act' : 'pref',
  'pos' : set(),
  'neg' : set(),
  'prefs' : {},
},
[
  'Huh?',
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
  
  nlg_pos = 0
  nlg_neg = 0
  try:
    NLU.NLU(data)
  except Exception as err:
    print 'NLU failed on', utterance
    print err
  else:
    print 'NLU:'
    print data
  try:
    DM.DM(nlu_dm)
  except Exception as err:
    print 'DM failed on', utterance
    print err
  else:
    print 'DM'
    print nlu_dm
  try:
    NLG.NLG(dm_nlg)
  except Exception as err:
    print 'NLG failed on', utterance
    print err
    nlg_neg = nlg_neg + 1
  else:
    for out in outputs 
      if dm_nlg['output'] == out:	  
        nlg_pos = nlg_pos + 1
      else:
        nlg_neg = nlg_neg + 1
    print 'NLG'
    print 'NLG errors = ' + str(nlg_neg)
    print 'NlG corect = ' + str(nlg_pos)

