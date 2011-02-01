import MySQLdb
import os, sys
dbinfo = eval(open('dbinfo.txt').read())

try:
	conn = MySQLdb.connect(host=dbinfo['host'],
											user=dbinfo['user'],
											passwd=dbinfo['passwd'],
											db=dbinfo['db'])
except MySQLdb.Error, e:
	print 'Error %d: %s' % (e.args[0], e.args[1])
	sys.exit(1)

types = [
	'comp_cast_type',
	'company_type',
	'info_type',
	'kind_type',
	'link_type',
	'role_type',
]

type_map = {}

cur = conn.cursor()
for t in types:
	cur.execute('SELECT * FROM %s' % t)
	type_map[t] = {}
	for m in cur.fetchall():
		id, name = m
		type_map[t][id] = name

people = {}		
cur.execute('SELECT id, name FROM name WHERE imdb_index="I"')
rows = list(cur.fetchall())
for person_id, name in rows:
	people[name] = {}
	people[name]['person_id'] = person_id
	people[name]['info'] = {}
	cur.execute('SELECT * FROM person_info WHERE person_id="%s"' % person_id)
	infos = list(cur.fetchall())
	for id, person_id, info_type_id, info, note in infos:
		people[name]['info'][type_map['info_type'][info_type_id]] = info
	break

print people['Abrams, Sam']['info']['birth date']
cur.close()
conn.close()
