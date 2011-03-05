'''
Created on Feb 16, 2011

@author: gabrielsanchez
'''
import UnigramChunker

def main():
	
	chunker = UnigramChunker.UnigramChunker()
	
	try:
		import cPickle as pickle
	except:
		import pickle

	fh= open('eChunker.pkl', 'w')
	pickle.dump(chunker, fh)
	fh.close()

if __name__ == '__main__':
	main()