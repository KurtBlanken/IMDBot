#!/usr/bin/env python
import string
import imdb
import Get_Fuzzy

URI = 'mysql://root:team5@localhost/imdb'
id = 'console'
imdb_access = imdb.IMDb('sql', uri=URI)
movie1 = raw_input('Movie 1: ')
movie2 = raw_input('Movie 2: ')
movie1 = imdb_access.search_movie(movie1)
movie2 = imdb_access.search_movie(movie2)
movie1 = Get_Fuzzy.get_movie(movie1)
movie2 = Get_Fuzzy.get_movie(movie2)
response = Get_Fuzzy.get_closeness(imdb_access, movie1, movie2)

print 'Difference factor between ',movie1,
print '\n',' and ',movie2,': ',response,'\n'
