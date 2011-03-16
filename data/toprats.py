RatingsIn = open('movies_with_ratings.txt','r')
TopIn = open('title_index.txt','r')
out = open('top_movies_with_ratings.txt','w')

top_movies = []
rat_movies = []
top_rat_movies = []
for movie in RatingsIn.readlines():
   rat_movies.append(int(movie))
   
for movie in TopIn.readlines():
   m = movie.split()
   imdbID = int(m[0])
   del m[0]
   title = ''
   for thing in m:
      title += thing + ' '
   top_movies.append([imdbID, title])

for movie in top_movies:
   if movie[0] in rat_movies:
      top_rat_movies.append(movie)
      
top_rat_movies.sort(key=lambda x: x[1])
for movie in top_rat_movies:
   out.write(str(movie[0]) + ' ' + movie[1] + '\n')

RatingsIn.close()
TopIn.close()
out.close()
