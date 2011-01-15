#!/usr/bin/env python
import os, sys
from threading import Thread
import subprocess
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
	utterance = sys.stdin.readline().strip()
	if 'uptime' in utterance:
		utterance = subprocess.Popen(["uptime"], stdout=subprocess.PIPE).communicate()[0].strip()
	elif 'hostname' in utterance:
		utterance = subprocess.Popen(["hostname"], stdout=subprocess.PIPE).communicate()[0].strip()
	elif 'date' in utterance:
		utterance = subprocess.Popen(["date"], stdout=subprocess.PIPE).communicate()[0].strip()
	else:
		utterance = NLG.get_utterance(id, Planner.get_knowledge_or_question(id, NLU.get_meaning(utterance)))
	sys.stdout.write(utterance + '\n')
	sys.stdout.flush()
	
os.remove('/tmp/imdbot_pid')
