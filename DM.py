import trivia
import preferences
user_prefs = {}

def DM(data):
  # initialize prefs for user if they don't exist yet
  
  if data['id'] not in user_prefs:
    user_prefs[data['id']] = { 'pos' : set(), 'neg' : set(), 'prefs' : {}, 'recs' : get_initial_recs()}
  if data['act'] == 'pref':
    newData = data
    data['pos'].union(user_prefs[data['id']]['pos'])
    data['neg'].union(user_prefs[data['id']]['neg'])
    for key, value in user_prefs[data['id']]['prefs'].items():
      data['prefs'][key] = value
    preferences.handle(user_prefs, newData)
  elif data['act'] == 'trivia':
    trivia.handle(data)
  
  NLG.NLG(data)
  
def get_introduction():
  return "Welcome to IMDBot"
  
def get_initial_recs():
   top100_in = open('top100.txt', 'r')
   top100 = []
   while True:
      line = top100_in.readline()
      if line == '':
         break
      movie = int(line.split()[0])
   # change this to appropriate accessor
      movie = imdbi.get_movie(movie)
      top100.append([movie,0])

   top100_in.close()
   return top100
