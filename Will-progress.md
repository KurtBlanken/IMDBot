I have finished the difference generator (inside of Get_Fuzzy.py), though the weights can stll be changed around.
Pickle_Recs.py will run through movies in title_index.txt and output the 5 closest. Currently it runs an n^2 query on the movies, but a better solution is possible.

------ 3/6/2011 -------
get_initial_recs() added to DM.py
on line 30: need use appropriate imdb database accessor for get_movie
current list is 100, if this causes performance issues it should be lowered

preferences.py added
single entry-point function handle added
call to preferences added to DM.py line 15 (is this correct?)
Not sure if access of data from user_prefs is correct
should handle actor, movie
