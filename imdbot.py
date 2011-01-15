#!/usr/bin/env python
import os, sys
from threading import Thread
import NLU, Planner, NLG

try:
	os.remove("/tmp/imdbot_pid")
except:
	pass
	
pid_file = open("/tmp/imdbot_pid", 'w')
pid_file.write("{0}\n".format(os.getpid()))
pid_file.close()

# input
r1, w1 = os.pipe()
pipe1_r = os.fdopen(r1, 'r')
pipe1_w = os.fdopen(w1, 'w')
# output
r2, w2 = os.pipe()
pipe2_r = os.fdopen(r2, 'r')
pipe2_w = os.fdopen(w2, 'w')

class Redirect(Thread):
   def __init__ (self, r, w, sendId=False):
   	Thread.__init__(self)
   	self.setDaemon(True)
   	self.r = r
   	self.w = w
   	self.sendId = sendId
   def run(self):
   	while 1:
   		line = self.r.readline()
   		if self.sendId:
   			if line == "":
   				self.w.write("-1\n")
   			else:
   				self.w.write("console\n")
   		self.w.write(line)
   		self.w.flush()
   	
Redirect(sys.stdin, pipe1_w, sendId=True).start()
Redirect(pipe2_r, sys.stdout).start()

while 1:
	id = pipe1_r.readline().strip()
	if id == "-1":
		break
	utterance = pipe1_r.readline().strip()
	utterance = NLG.get_utterance(id, Planner.get_knowledge_or_question(id, NLU.get_meaning(utterance)))
	pipe2_w.write(utterance + "\n")
	pipe2_w.flush()
	
os.remove("/tmp/imdbot_pid")
