import NLG, trivia
user_prefs = {}

def DM(data):
  # initialize prefs for user if they don't exist yet
  
  if data['id'] not in user_prefs:
    user_prefs[data['id']] = { 'pos' : set(), 'neg' : set(), 'prefs' : {}, 'recs' : get_initial_recs()}
  if data['act'] == 'pref':
    data['pos'].union(user_prefs[data['id']]['pos'])
    data['neg'].union(user_prefs[data['id']]['neg'])
    for key, value in user_prefs[data['id']]['prefs'].items():
      data['prefs'][key] = value
  elif data['act'] == 'trivia':
    trivia.handle(data)
  
  NLG.NLG(data)
  
def get_introduction():
  return "Welcome to IMDBot"
  
def get_initial_recs():
	return []
