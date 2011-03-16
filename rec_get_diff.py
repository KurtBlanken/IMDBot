#!/usr/bin/env python
import string
import imdbi

# numbers that can increase difference
RATING_WEIGHT = 2.0
VOTE_DIST_WEIGHT = 10.0
MPAA_R_WEIGHT = 3.0

# numbers that decrease difference (must be < 1)
MPAA_WEIGHT = .3
GENRE_WEIGHT = .6
ACTOR_WEIGHT = .02 # increase based on preferences or whatever
WRITER_WEIGHT = .5
DIRECTOR_WEIGHT = .6

MOVIE_VAL = 60

ratings = {'G': 0, 'PG': 1, 'PG-13': 2, 'R': 3, 'NC-17': 10, 'UR': 11}
needed_keys = ['votes_distribution', 'rating', 'genres', 'mpaa', 'cast', 'writer', 'director']

def get_closeness(movie1, movie2):
	# the difference value, 0 = most similar
	diff = 50
	i = 0
	# ratings
	key = 0
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		print type(movie2['votes_distribution'])
		while i < 10:
			ratingA = movie1['votes_distribution'][i]
			ratingB = movie2['votes_distribution'][i]
			print ratingA,' ',ratingB
			diff += abs(float(ratingA) - float(ratingB)) * VOTE_DIST_WEIGHT
			i += 1
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		# print type(movie2['rating']),' ',movie2['rating']
		diff += abs(float(movie1['rating'][0]) - float(movie2['rating'][0])) * RATING_WEIGHT
	
	# genres
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		for genre in movie1['genres']:
			if genre in movie2['genres']:
				diff -= (diff * GENRE_WEIGHT)
			
	# keywords?
	# actually parsing these could be really inefficient
	
	# mpaa
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key] 
	else:
		mpaa1 = movie1['mpaa'][0].split()
		mpaa2 = movie2['mpaa'][0].split()
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
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		for actor in movie1['cast']:
			if actor in movie2['cast']:
				diff -= (diff * ACTOR_WEIGHT)
	# writers
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		for actor in movie1['writer']:
			if actor in movie2['writer']:
				diff -= (diff * WRITER_WEIGHT)
	# director
	key += 1
	if needed_keys[key] not in movie1 or needed_keys[key] not in movie2:
		print movie2['title'],' Missing Key ',needed_keys[key]
	else:
		for director in movie1['director']:
			if actor in movie2['director']:
				diff -= (diff * DIRECTOR_WEIGHT)
	# studio?
	# characters?
	return diff;

# Get the movies to compare it to, generating top 5
# should already be imdbi objects
def get_top_x(movie_prime, comparelist):
	weightedcompare = []
	weightedcompare.append([movie_prime['id'], movie_prime['title'], 0])
	for movie in comparelist:
		diff = get_closeness(movie_prime, movie)
		weightedcompare.append([movie['id'], movie['title'], diff])
	weightedcompare.sort(key = lambda x: x[2])
	# change diff into pref weights
	i = MOVIE_VAL
	for movie in weightedcompare:
		movie[2] = i
		i -= 1
	
	#weightedcompare.sort(key = lambda x: x[2], reverse=True)
	return weightedcompare
