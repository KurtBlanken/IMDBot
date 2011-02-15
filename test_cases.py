# utterance
utterance = 'When was Armageddon made?'
# NLU output / dialog manager input
nlu_dm = {	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'when',
			'entity' : ('movie', 48368),
		}]
}
# dialog manager output / NLG input
dm_nlg = {	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'when',
			'entity' : ('movie', 48368),
			'answer' : 1998,
		}]
}
output = [
	'1998.',
	'The production year was 1998.',
]

# utterance
utterance = 'Was Matt Damon in Armageddon?'
# NLU output / dialog manager input
nlu_dm = {	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
			'entities' : [('person', 260886), ('movie', 48368)],
		}]
}
# dialog manager output / NLG input
dm_nlg = {	'act' : 'trivia',
	'trivias' : [
		{	'attr' : 'in',
			'entities' : [('person', 260886), ('movie', 48368)],
			'answer' : False,
		}]
}
output = [
	'No.',
	"I don't think so.",
]

# utterance
utterance = 'I think Danny DeVito is hilarious'
# NLU output / dialog manager input
nlu_dm = {	'act' : 'pref',
	'pos' : [('actor', 291778)],
	'neg' : [],
}
# dialog manager output / NLG input
dm_nlg = {	'act' : 'pref',
	'pos' : [('actor', 291778)],
	'neg' : [],
	'prefs' : set(('actor', 291778)),
}
output = [
	'Ok.',
	'I agree.',
]

# utterance
utterance = 'I think Fubie Fubar is hilarious'
# NLU output / dialog manager input
nlu_dm = {	'act' : 'pref',
	'pos' : [],
	'neg' : [],
}
# dialog manager output / NLG input
dm_nlg = {	'act' : 'pref',
	'pos' : [],
	'neg' : [],
	'prefs' : None,
}
output = [
	"I don't understand.",
	"I don't know about Fubie Fubar.",
	"Huh?",
]
