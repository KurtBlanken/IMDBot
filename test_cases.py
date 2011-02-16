cases = [
(
# utterance
'When was Armageddon made?',
# NLU output / dialog manager input
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'when',
			'entity' : ('movie', 48368),
		}]
},
# dialog manager output / NLG input
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'when',
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
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
			'entities' : [('person', 260886), ('movie', 48368)],
		}]
},
# dialog manager output / NLG input
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
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
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
			'entities' : [('person', 8590), ('movie', 48368)],
		}]
},
# dialog manager output / NLG input
{	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
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
'I think Danny DeVito is hilarious',
# NLU output / dialog manager input
{	'act' : 'pref',
	'pos' : [('actor', 291778)],
	'neg' : [],
},
# dialog manager output / NLG input
{	'act' : 'pref',
	'pos' : [('actor', 291778)],
	'neg' : [],
	'prefs' : set(('actor', 291778)),
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
{	'act' : 'pref',
	'pos' : [],
	'neg' : [],
},
# dialog manager output / NLG input
{	'act' : 'pref',
	'pos' : [],
	'neg' : [],
	'prefs' : None,
},
[
	"I don't understand.",
	"I don't know about Fubie Fubar.",
	"Huh?",
]
),
] # end cases

## PYTHON CODE ##
import trivia
from imdbi import IMDBInterface
imdbi = IMDBInterface()
lines = open('test_cases.py').readlines()
end = 0
for i, line in enumerate(lines):
	if '## PYTHON CODE ##' in line:
		end = i-1
lines = filter(line.strip, lines[:end])
d = {}
exec ''.join(lines) in d
for utterance, nlu_dm, dm_nlg, outputs in d['cases']:
	nlu_dm['imdbi'] = imdbi
	dm_nlg['imdbi'] = imdbi
	print '> ' + utterance
	if nlu_dm['act'] == 'trivia':
		trivia.handle(nlu_dm)
		print 'trivia handler says:'
		print nlu_dm
