'''
Created on Feb 16, 2011

@author: gabrielsanchez
'''
import nltk

class UnigramChunker(nltk.chunk.ChunkParserI):
	def __init__(self):
		train_data = [[(t, c) for w, t, c in nltk.chunk.tree2conlltags(sent)]
									for sent in nltk.corpus.conll2000.chunked_sents()]
		self.tagger = nltk.UnigramTagger(train_data)
	def parse(self, sentence):
		pos_tags = [pos for (word, pos) in sentence]
		tagged_pos_tags = self.tagger.tag(pos_tags)
		chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
		conlltags = [(word, pos, chunktag) for ((word, pos), chunktag) in zip(sentence, chunktags)]
		return nltk.chunk.conlltags2tree(conlltags)