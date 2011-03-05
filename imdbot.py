#!/usr/bin/env python
import os, sys
from threading import Thread
import subprocess
import json
import NLU, DM, NLG

server = False
if len(sys.argv) > 1 and sys.argv[1] == 'server':
  print "starting server..."
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

if not server:
  import readline
  try:
      readline.read_history_file('hist')
  except IOError:
      pass
  import atexit
  atexit.register(readline.write_history_file, 'hist')
  print DM.get_introduction()
while 1:
  if server:
    id = sys.stdin.readline().strip()
    user_utterance = sys.stdin.readline().strip()
  else:
    id = 'console'
    try:
      user_utterance = raw_input('> ')
    except EOFError:
      print "\ngoodbye"
      sys.exit(0)
  data = {
    'id' : id,
    'user_utterance' : user_utterance,
    'prefs' : set(),
    'errors' : [],
  }
  NLU.NLU(data)
  DM.DM(data)
  NLG.NLG(data)
  for key, value in data.items():
    if type(value) == type(set()):
      data[key] = list(value)
  #print data
  result = json.dumps(data)
  if server:
    sys.stderr.write('> ' + user_utterance + '\n')
    sys.stderr.write('< ' + result + '\n')
  sys.stdout.write(result + '\n')
  sys.stdout.flush()
  
os.remove('/tmp/imdbot_pid')
