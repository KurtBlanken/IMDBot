user_prefs = {}

def DM(data):
	# initialize prefs for user if they don't exist yet
	if data['id'] not in user_prefs:
		user_prefs[data['id']] = set()
	data['prefs'] = data['prefs'].union(user_prefs[data['id']])
	if data['act'] == 'pref':
		handle_pref(data)
	
def handle_pref(data):
	user_prefs[data['id']] = user_prefs[data['id']].union(data['prefs'])
	
def get_introduction():
	return "Welcome to IMDBot"
