#!/usr/bin/env python
import string
import imdb

# numbers that can increase difference
RATING_WEIGHT = 2.0
VOTE_DIST_WEIGHT = 2.0
MPAA_R_WEIGHT = 3.0

# numbers that decrease difference (must be < 1)
MPAA_WEIGHT = .25
GENRE_WEIGHT = .5
ACTOR_WEIGHT = .02 # increase based on preferences or whatever
WRITER_WEIGHT = .45
DIRECTOR_WEIGHT = .45

ratings = {'G': 0, 'PG': 1, 'PG-13': 2, 'R': 3, 'NC-17': 10, 'UR': 11}
required_keys = ('votes distribution','rating','genres','mpaa','cast','writer','director')

def get_closeness(imdb, movie1, movie2):
   # Should already be updated
   #imdb.update(movie1, 'all')
   #imdb.update(movie2, 'all')

   # needs correct keys
   for key in required_keys:
      if key not in movie1.keys() or key not in movie2.keys():
         return 100
   # the difference value, 0 = most similar
   diff = 50
   i = 0
   # ratings
   while i < 10:
      ratingA = movie1['votes distribution'][i]
      ratingB = movie2['votes distribution'][i]
      try:
         ratingA = float(ratingA)
      except ValueError:
         ratingA = 0.0
      try:
         ratingB = float(ratingA)
      except ValueError:
         ratingB = 0.0
      diff += abs(ratingA - ratingB) * VOTE_DIST_WEIGHT
      i += 1
   diff += abs(movie1['rating'] - movie2['rating']) * RATING_WEIGHT
   
   # genres
   for genre in movie1['genres']:
      if genre in movie2['genres']:
         diff -= (diff * GENRE_WEIGHT)
         
   # keywords?
   # actually parsing these could be really inefficient
   
   # mpaa
   mpaa1 = movie1['mpaa'].split()
   mpaa2 = movie2['mpaa'].split()
   mpaa1.pop(0)
   mpaa2.pop(0)
   mpaa1.pop(1)
   mpaa2.pop(1)
   diff += abs(ratings[mpaa1[0]] - ratings[mpaa2[0]]) * MPAA_R_WEIGHT
   mpaa1.pop(0)
   mpaa2.pop(0)
   # mpaa reasons
   # IMPLEMENT syn sets (frigtening imagery, scary images, etc.)
   for reason in mpaa1:
      if reason != 'and' and reason != 'some':
         if reason in mpaa2:
            diff -= (diff * MPAA_WEIGHT)
            
   # actors are not in any particular order
   for actor in movie1['cast']:
      if actor in movie2['cast']:
         diff -= (diff * ACTOR_WEIGHT)
   # writers
   for actor in movie1['writer']:
      if actor in movie2['writer']:
         diff -= (diff * WRITER_WEIGHT)
   # director
   for director in movie1['director']:
      if actor in movie2['director']:
         diff -= (diff * DIRECTOR_WEIGHT)
   # studio?
   # characters?
   

   return diff;
   
# in my current database, first result is not necessarily a movie
def get_movie(movie):
   for m in movie:
      if m['kind'] == 'movie':
         return m
   return 'void movie'
