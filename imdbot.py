#!/usr/bin/env python
import os, sys
from threading import Thread
import subprocess
import json
import NLU, Planner, NLG

server = False
if len(sys.argv) > 1 and sys.argv[1] == 'server':
	server = True
	try:
		os.remove('/tmp/imdbot_pid')
	except:
		pass
	
	pid_file = open('/tmp/imdbot_pid', 'w')
	pid_file.write("{0}\n".format(os.getpid()))
	pid_file.close()

	# input
	r, _ = os.pipe()
	sys.stdin = os.fdopen(r, 'r')
	# output
	_, w = os.pipe()
	sys.stdout = os.fdopen(w, 'w')

while 1:
	if server:
		id = sys.stdin.readline().strip()
	else:
		id = 'console'
	user_utterance = sys.stdin.readline().strip()
	meaning = NLU.get_meaning(user_utterance)
	response = Planner.get_response(id, meaning)
	utterance = NLG.get_utterance(id, response)
	result = json.dumps({
		'id' : id,
		'user_utterance' : user_utterance,
		'meaning' : meaning,
		'response' : response,
		'utterance' : utterance})
	sys.stdout.write(result + '\n')
	sys.stdout.flush()
	
os.remove('/tmp/imdbot_pid')
