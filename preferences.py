# some definitions
REC_LEN = 100
MAX_CONFIDENCE = 100
ACTOR_VAL = 30
DIRECTOR_VAL = 60
WRITER_VAL = 60

movie_obj = 0
movie_confidence = 1
pref_type = 0
pref_obj = 1

# the main function
def handle(user_prefs, newData):
   # add preferences to the recommendation list
   for pref in newData['pos']:
      # handle actor
      # currently just upps movies currently in list
      if pref[pref_type] == 'actor':
         notfound = True
         for movie in user_prefs['recs']:
            if pref[pref_obj] in movie[movie_obj]['cast']
               movie[movie_confidence] += ACTOR_VAL
               notfound = False
               break
      # handle movie
      elif pref[pref_type] == 'movie':
         notfound = True
         for movie in user_prefs['recs']:
            if movie[movie_obj] == pref[pref_obj]
               movie[movie_confidence] += 90
               notfound = False
               break
         if notfound:
            user_prefs['recs'].append([pref[pref_obj], 90)
   
   
   
   # remove antipreferences from the recommendation list
   # this can be a not very efficient thing
   for movie in user_prefs['recs']:
      for antipref in user_prefs['neg']:
         # handle actor
         if antipref[pref_type] == 'actor':
            if antipref[pref_obj] in movie[movie_obj]['cast']:
               movie[movie_confidence] -= ACTOR_VAL
         # handle movie
         elif antipref[pref_type] == 'movie':
            if antipref[pref_obj] == movie[movie_obj]:
               movie[movie_confidence] -= MAX_CONFIDENCE
               
   # cull
   # sort, then cut bottom
   user_prefs['recs'].sort(key=lambda confidence: confidence[movie_confidence], reverse=True)
   del user_prefs['recs'][REC_LEN:]
