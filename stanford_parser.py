#!/usr/bin/env jython
import os, sys
JAVA = False
if os.name == 'java':
	JAVA = True
	sys.path.append('./lib/stanford-parser.jar')
	sys.path.append('./lib/jyson-1.0.1.jar')
	from java.io import CharArrayReader
	from edu.stanford.nlp import *
	from com.xhaus.jyson import JysonCodec as json
else:
	import json
	import nltk
import re
import socket

class StanfordParser:
	def __init__(self):
		if JAVA:
			self.lp = parser.lexparser.LexicalizedParser('./lib/englishPCFG.ser.gz')
			self.tlp = trees.PennTreebankLanguagePack()
			self.lp.setOptionFlags(["-maxLength", "80", "-retainTmpSubcategories"])

	def parse(self, sentence):
		if JAVA:
			return self._java_parse(sentence)
		return self._py_parse(sentence)

	def _py_parse(self, sentence):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect(('127.0.0.1', 10000))
		self.s.send(sentence)
		self.s.send('\n')
		out = json.loads(recv_string(self.s))
		self.s.close()
		tree, deps = out
		return build_nltk_tree(tree), deps
		
	def _java_parse(self, sentence):
		toke = self.tlp.getTokenizerFactory().getTokenizer(CharArrayReader(sentence));
		wordlist = toke.tokenize()
		 
		if (self.lp.parse(wordlist)):
			tree = self.lp.getBestParse()
		 
			gsf = self.tlp.grammaticalStructureFactory()
			gs = gsf.newGrammaticalStructure(tree)
			tdl = gs.typedDependenciesCollapsed()

		return tree, tdl
		
'''
@param tree: The tree dict generated from the Stanford Parser 
'''
def tree_to_string(tree):
	if len(tree['children']) > 0:
		brackets = "(" + tree['label'] + " "
	else:
		brackets = tree['label']
	for child in tree['children']:
		brackets += tree_to_string(child)
	if len(tree['children']) > 0:
		brackets += ")"
	return brackets

'''
@param tree: The tree dict generated from the Stanford Parser 
'''
def build_nltk_tree(tree):
	brackets = tree_to_string(tree)
	return nltk.tree.bracket_parse(brackets)

def recv_string(conn):
	s = ''
	while 1:
		c = conn.recv(1)
		if c == '\n':
			break
		s += c
	return s
	
def tree_to_dict(tree, d={}):
	d['label'] = str(tree.label())
	d['children'] = []
	for child in tree.children():
		d['children'].append({})
		tree_to_dict(child, d['children'][-1])
	return d

depre = re.compile('([a-z_]+)\(([^-]+)-([0-9]+), ([^-]+)-([0-9]+)\)')

if __name__ == '__main__':
	parser = StanfordParser()
	if JAVA:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(('127.0.0.1', 10000))
		s.listen(1)
		while 1:
			conn, addr = s.accept()
			tree, tdl = parser.parse(recv_string(conn))
			deps = [depre.match(str(dep)).groups() for dep in tdl]
			tree_dict = tree_to_dict(tree)
			conn.send(json.dumps((tree_dict, deps)))
			conn.send('\n')
			conn.close()
		s.close()
	else:
		tree, deps = parser.parse('I just saw Tron Legacy, it was pretty good but the lead sucked.')
