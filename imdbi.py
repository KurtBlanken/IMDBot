import MySQLdb
import os, sys

dbinfo = eval(open('dbinfo.txt').read())

try:
	conn = MySQLdb.connect(host='127.0.0.1',
												 user=dbinfo['user'],
												 passwd=dbinfo['passwd'],
												 db=dbinfo['db'])
except:
	conn = MySQLdb.connect(host=dbinfo['host'],
												 user=dbinfo['user'],
												 passwd=dbinfo['passwd'],
												 db=dbinfo['db'])

cur = conn.cursor()

cur.execute('show tables')
table_names = [r[0] for r in cur.fetchall()]
tables = {}
type_map = {}
for table in table_names:
	cur.execute('desc {0}'.format(table))
	tables[table] = [r[0] for r in cur.fetchall()]
	if 'type' in table:
		col_name = table + '_id'
		if table == 'kind_type':
			col_name = 'kind_id'
		elif table == 'role_type':
			col_name = 'role_id'
		type_map[col_name] = (table, {})
		cur.execute('SELECT * FROM {0}'.format(table))
		res = cur.fetchall()
		for id, kind in res:
			type_map[col_name][1][id] = kind

def get_movie(id):
	cur.execute('SELECT * FROM title WHERE id={0}'.format(id))
	res = cur.fetchall()
	assert len(res) == 1
	res = res[0]
	d = {}
	add_res_to_dict(tables['title'], res, d)
	cur.execute('SELECT * FROM movie_info WHERE movie_id={0}'.format(d['id']))
	res = cur.fetchall()
	for r in res:
		d2 = {}
		add_res_to_dict(tables['movie_info'], r, d2)
		if d2['info_type'] not in d:
			d[d2['info_type']] = []
		d[d2['info_type']].append(d2['info'])
	d['cast'] = get_cast_info(id)
	d['actors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actor', d['cast'])
	d['actresses'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actress', d['cast'])
	d['writers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'writer', d['cast'])
	d['directors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'director', d['cast'])
	d['producers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'producer', d['cast'])
	return d
	
def get_cast_info(id):
	cur.execute('SELECT * FROM cast_info WHERE movie_id={0}'.format(id))
	res = cur.fetchall()
	cast_info = []
	for r in res:
		d2 = {}
		add_res_to_dict(tables['cast_info'], r, d2)
		cast_info.append(d2)
		cur.execute('SELECT * FROM name WHERE id={0}'.format(d2['person_id']))
		r2 = cur.fetchall()
		assert len(r2) == 1
		r2 = r2[0]
		d3 = {}
		add_res_to_dict(tables['name'], r2, d3)
		d2['name'] = d3['name']
	def keyfn(d):
		if 'nr_order' not in d:
			return 100
		return d['nr_order']
	cast_info.sort(key=keyfn)
	return cast_info
	
def get_person(id):
	pass

def add_res_to_dict(col_names, res, d):
	for k, v in zip(col_names, res):
		if v != None:
			if k in type_map and v in type_map[k][1]:
				v = type_map[k][1][v]
				k = type_map[k][0]
			d[k] = v
	return d

'''
titles = [line.split(' ', 1) for line in open('title_index.txt').readlines()]
for id, title in titles:
	m = get_movie(id)
	if 'actresses' in m and len(m['actresses']) > 0:
		lead = m['actresses'][0]
		print lead['person_id'], lead['name']
'''

'''
for id, title in titles:
	m = get_movie(id)
	print m.keys()
'''

'''
cur.execute('SELECT id, title FROM title')
titles = list(cur.fetchall())
print >> sys.stderr, len(titles)
for i, (id, title) in enumerate(titles):
	print >> sys.stderr, i / float(len(titles))
	m = get_movie(id)
	if 'title' in m and m['kind_type'] == 'movie' and 'mpaa' in m:
		print id, m['title']
		sys.stdout.flush()
'''

#ids = [line.split(' ')[0] for line in open('adult.2.ids', 'r').readlines()]


#for movie_id in ids:
#	cur.execute('DELETE FROM title WHERE id={0}'.format(movie_id))

#cur.execute('SELECT id, title FROM title')
#titles = list(cur.fetchall())
#for i, (id, title) in enumerate(titles):
#	cur.execute('SELECT * FROM movie_info WHERE movie_id={0}'.format(id))
#	if len(cur.fetchall()) == 0:
#		print >> sys.stderr, id, title
#	print i / float(len(titles))

#for movie_id in adult_movies:
#	cur.execute('DELETE FROM movie_info WHERE movie_id={0}'.format(movie_id))
#print len(adult_movies)
