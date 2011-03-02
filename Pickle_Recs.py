#!/usr/bin/env python
import string
import imdb
import Get_Fuzzy
import cPickle

# setting things up
URI = 'mysql://root:team5@localhost/imdb'
id = 'console'
imdb_access = imdb.IMDb('sql', uri=URI)
DEFAULT_MOVIE = ('DEFAULT MOST DIFFERENT MOVIE', 100, 0)
Movie_list_master = open("title_index.txt", "r")
Rec_Out = open("recommendations.txt", "w")

# the diff comparing for loop
# the primary movie
for i in range(10):
   # movies are taken from the title_index.txt
   movie_id_master = int(Movie_list_master.readline().split()[0])
   movie1 = imdb_access.get_movie(movie_id_master)
   print 'Processing movie #',i,': ',movie1['title']
   top5 = [DEFAULT_MOVIE]
   Movie_list_parser = open("title_index.txt", "r")
   
   #movies being compared to the primary movie
   for j in range(100):
      movie_id_parser = int(Movie_list_parser.readline().split()[0])
      # don't compare a movie to itself! not fair
      if movie_id_parser == movie_id_master:
         continue
      movie2 = imdb_access.get_movie(movie_id_parser)
      # this is where the magic happens
      # get diff
      response = Get_Fuzzy.get_closeness(imdb_access, movie1, movie2)
      # see if it belongs in the top 5
      for m in top5:
         if response < m[1]:
            top5.append((movie2['title'], response, movie2.movieID))
            break
   
   # done: time to cut down the top 5 and print out the recommendations to 
   # the output file
   # movieID title|movieID1 title1|movieID2 title2|movieID3 title3|movieID4 title4|movieID5 title5
   # when reading, split around '|'
   Movie_list_parser.close()       
   top5.sort(key=lambda diff: diff[1])
   del top5[5:]
   Rec_Out.write(str(movie1.movieID) + ' ' + movie1['title'])
   for movie in top5:
      Rec_Out.write('|'+ str(movie[2]) + ' ' + movie[0])
   Rec_Out.write('\n')
   
Movie_list_master.close()
Rec_Out.close()
