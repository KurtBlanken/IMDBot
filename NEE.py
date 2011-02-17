import nltk, re
import Levenshtein as lev

''' Levenshtein examples:
jaro(string1, string2)

    The Jaro string similarity metric is intended for short strings like
    personal last names.  It is 0 for completely different strings and
    1 for identical strings.
    
ratio(string1, string2)
    
    The similarity is a number between 0 and 1, it's usually equal or
    somewhat higher than difflib.SequenceMatcher.ratio(), because it's
    based on real minimal edit distance.
'''

def insert(s, i, d):
	if s[0] not in d:
		d[s[0]] = ([], {})
	if len(s) == 1:
		d[s[0]][0].append(i)
	else:
		insert(s[1:], i, d[s[0]][1])

titles = [line.strip().split(' ', 1)
						for line in open('title_index.txt').readlines()]
d = {}
for id, title in titles:
	insert(title, id, d)

def lookup(s, d):
	if len(s) == 1:
		return d[s][0]
	return lookup(s[1:], d[s[0]][1])

def query(s):
	results = []
	for id, title in titles:
		l = lev.ratio(s, title)
		results.append((l, id, title))
	results.sort(key=lambda r: r[0], reverse=True)
	return results

def pairs(lst):
	i = iter(lst)
	first = prev = i.next()
	for item in i:
		yield prev, item
		prev = item
	yield item, first


''' 
Uses ne_chunker
'''


def getEntities(sentence):
	
	
	tagged_sent= nltk.pos_tag(nltk.word_tokenize(sentence))
	tree= nltk.ne_chunk(tagged_sent)
	
	print tagged_sent
	
	print tree
	
	
	""" Entities is a list of lists to facilitate pairing
	 	  with multiple entities in a sentence
	"""
	entities=[]
	for subtree in tree.subtrees():
		if subtree.node == 'PERSON':
			nelist=[]
			for child in subtree:
				name,tag = child
				if tag == 'NNP': nelist.append(name)
			if len(nelist) > 0: entities.append(nelist)
		
		
	actors = [line.split(" ", 1) for line in open('actors_index.txt').readlines()]
		
	
	print entities
		
	matches= {}
	for list in entities:
		for pair in pairs(list):
			first, last= pair
			name= first + ' ' + last
			print name
			ratios = []
			for id, actor in actors:
				s= actor.strip().replace(' ', '').split(',')
				if len(s) == 1:
					actor= s[0]
				else:
					actor = s[1] + ' ' + s[0]
				ratio= lev.jaro(name,actor)
				if ratio >= 0.9:
					ratios.append((ratio,id,actor))
			ratios.sort(key=lambda x: x[0], reverse= True)
			if len(ratios) > 0:
				r, id, actor = ratios[0]
				matches[pair] = {'id':id, 'name': actor, 'class': 'actor'}
	return matches

def main():
	
	sentences = [
	"What movies have Bill Murray and Danny DeVito been in together?",
	"Danny DeVito is funny.",
	#"I like racing car movies like Gone in 60 Seconds.",
	"What about something with Nicole Kidman?",
	"Where is James Cameron?",
	"I hate Sylvester Stallone",
	]
	
	for sent in sentences:
		entities=getEntities(sent)
		for ent in entities:
			first,last= ent
			name= first + ' ' + last
			print sent.replace(name, '(' + entities[ent]['class'] + ' ' + entities[ent]['id'] + ')')

if __name__ == '__main__':
	main()