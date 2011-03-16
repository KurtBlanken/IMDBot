#!/usr/bin/env python
import os, sys
import json
import NLU, DM
import imdbi

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
  print sys.stdin

imdb = imdbi.IMDBInterface()
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
    'imdbi' : imdb,
    'outputs' : [],
    'act' : None,
  }
  NLU.NLU(data)
  DM.DM(data)
  for key, value in data.items():
    if type(value) == type(set()):
      data[key] = list(value)
  NLU.add_entity_names(data)
  del data['imdbi']
  result = json.dumps(imdbi.clean_unicode_errors(data))
  if server:
    sys.stderr.write('> ' + user_utterance + '\n')
    sys.stderr.write('< ' + result + '\n')
  if server:
  	sys.stdout.write(result + '\n')
  else:
  	sys.stdout.write(result + '\n')
  	for output in data['outputs']:
  		sys.stdout.write(str(output) + '\n')
  sys.stdout.flush()  
  
os.remove('/tmp/imdbot_pid')
