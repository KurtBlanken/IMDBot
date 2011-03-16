import MySQLdb
import os, sys
from collections import defaultdict

class IMDBInterface(object):
	def __init__(self):
		dbinfo = eval(open('data/dbinfo.txt').read())

		try:
			conn = MySQLdb.connect(host='127.0.0.1',
														 user=dbinfo['user'],
														 passwd=dbinfo['passwd'],
														 db=dbinfo['db'],
														 connect_timeout=3)
		except:
			conn = MySQLdb.connect(host=dbinfo['host'],
														 user=dbinfo['user'],
														 passwd=dbinfo['passwd'],
														 db=dbinfo['db'],
														 connect_timeout=3)

		cur = conn.cursor()

		cur.execute('show tables')
		table_names = [r[0] for r in cur.fetchall()]
		tables = {}
		type_map = {}	
		self.col_map = {'kind_type':'kind_id','role_type':'role_id'}
		for table in table_names:
			cur.execute('desc {0}'.format(table))
			tables[table] = [r[0] for r in cur.fetchall()]
			if 'type' in table:
				if table in self.col_map:
					col_name = self.col_map[table]
				else:
					col_name = table + '_id'
				type_map[col_name] = (table, {})
				cur.execute('SELECT * FROM {0}'.format(table))
				res = cur.fetchall()
				for id, kind in res:
					type_map[col_name][1][id] = kind
		
		self.conn = conn
		self.cur = cur
		self.tables = tables
		self.type_map = type_map
		self.info_type_id = {}
		for key, value in self.type_map['info_type_id'][1].items():
			self.info_type_id[value] = key
		
		self.movie_cache = {}
		self.person_cache = {}

	def find_movie(self, keywords, directors=[], cast=[]):
		query = '"%{0}%"'.format('%'.join(keywords))
		self.cur.execute('SELECT id FROM title WHERE title LIKE {0}'.format(query))
		res = self.cur.fetchall()
		self.cur.execute('SELECT movie_id FROM aka_title WHERE title LIKE {0}'.format(query))
		res += self.cur.fetchall()
		movies = {}
		for (id,) in res:
			m = self.get_movie(id)
			if m and has_person(m, directors, "directors") and has_person(m, cast, "actors"):
				movies[id] = m
		return movies.values()
		
	def find_person(self, keywords):
		query = '"%{0}%"'.format('%'.join(keywords))
		self.cur.execute('SELECT id FROM name WHERE name LIKE {0}'.format(query))
		res = self.cur.fetchall()
		self.cur.execute('SELECT id FROM aka_name WHERE name LIKE {0}'.format(query))
		res += self.cur.fetchall()
		people = {}
		for (id,) in res:
			people[id] = self.get_person(id)
		return people.values()

	def get_movie(self, id, aka_info=True, movie_info=True, info_keys="*", cast_info=True):
		if id in self.movie_cache:
			return self.movie_cache[id]
		self.cur.execute('SELECT * FROM title WHERE id={0}'.format(id))
		res = self.cur.fetchall()
		if len(res) == 1:
			res = res[0]
			d = defaultdict(list)
			self._add_res_to_dict(self.tables['title'], res, d)
			if aka_info:
				query = 'SELECT title FROM aka_title WHERE movie_id={0}'.format(d['id'])
				self.cur.execute(query)
				res = self.cur.fetchall()
				d['akas'] = []
				for (title,) in res:
					d['akas'].append(title)
			if movie_info:
				query = 'SELECT * FROM movie_info WHERE movie_id={0}'.format(d['id'])
				if info_keys != "*":
					info_keys = ', '.join([str(self.info_type_id[key]) for key in info_keys])
					query += ' AND info_type_id IN ({0})'.format(info_keys)
				self.cur.execute(query)
				res = self.cur.fetchall()
				for r in res:
					d2 = {}
					self._add_res_to_dict(self.tables['movie_info'], r, d2)
					if d2['info_type'] not in d:
						d[d2['info_type']] = []
					d[d2['info_type']].append(d2['info'])
			if cast_info:
				d['cast'] = self.get_cast_info(id)
				for i, member in enumerate(d['cast']):
						member['formal_name'] = member['name']
						if len(member['formal_name'].split(",")) > 1:
							names = [name.strip() for name in member['formal_name'].split(",")]
							names.reverse()
							member['name'] = ' '.join(names)
						d['cast'][i] = member
				d['actors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actor', d['cast'])
				d['actresses'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actress', d['cast'])
				d['writers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'writer', d['cast'])
				d['directors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'director', d['cast'])
				d['producers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'producer', d['cast'])
			self.movie_cache[id] = d
			return d
		return None
	
	def get_cast_info(self, id):
		self.cur.execute('SELECT * FROM cast_info WHERE movie_id={0}'.format(id))
		res = self.cur.fetchall()
		cast_info = []
		for r in res:
			d2 = {}
			self._add_res_to_dict(self.tables['cast_info'], r, d2)
			cast_info.append(d2)
			self.cur.execute('SELECT * FROM name WHERE id={0}'.format(d2['person_id']))
			r2 = self.cur.fetchall()
			assert len(r2) == 1
			r2 = r2[0]
			d3 = {}
			self._add_res_to_dict(self.tables['name'], r2, d3)
			d2['name'] = d3['name']
		def keyfn(d):
			if 'nr_order' not in d:
				return 100
			return d['nr_order']
		cast_info.sort(key=keyfn)
		return cast_info
	
	def get_person(self, id, cast_info=True):
		if id in self.person_cache:
			return self.person_cache[id]
		self.cur.execute('SELECT * FROM name WHERE id={0}'.format(id))
		res = self.cur.fetchall()
		assert len(res) == 1
		res = res[0]
		d = {}
		self._add_res_to_dict(self.tables['name'], res, d)
		if cast_info:
			self.cur.execute('SELECT * FROM cast_info WHERE person_id={0}'.format(id))
			res = self.cur.fetchall()
			for r in res:
				d2 = {}
				self._add_res_to_dict(self.tables['cast_info'], r, d2)
				if 'role_type' in d2:
					if d2['role_type'] not in d:
						d[d2['role_type']] = set()
					d[d2['role_type']].add(d2['movie_id'])
		d['formal_name'] = d['name']
		if len(d['formal_name'].split(",")) > 1:
			names = [name.strip() for name in d['formal_name'].split(",")]
			names.reverse()
			d['name'] = ' '.join(names)
		self.person_cache[id] = d
		return d
		
	def get_movies(self):
		self.cur.execute('SELECT id, title FROM title')
		return self.cur.fetchall()
		
	def get_persons(self):
		self.cur.execute('SELECT id, name FROM name WHERE imdb_index="I" OR imdb_index IS NULL')
		return self.cur.fetchall()
	
	def add_rating(self, m, rating):
		self.cur.execute("SELECT count(*) FROM movie_info WHERE movie_id={0} AND info_type_id={1}".format(m['id'], 197))
		res = self.cur.fetchall()
		if res[0][0] == 0:
			self.cur.execute("INSERT INTO movie_info (movie_id, info_type_id, info) VALUES ({0}, {1}, '{2}')".format(m['id'], 197, rating[0]))
			self.cur.execute("INSERT INTO movie_info (movie_id, info_type_id, info) VALUES ({0}, {1}, '{2}')".format(m['id'], 199, rating[1]))
			self.cur.execute("INSERT INTO movie_info (movie_id, info_type_id, info) VALUES ({0}, {1}, '{2}')".format(m['id'], 201, rating[2]))
			
	def delete_movie(self, m):
		self.cur.execute("DELETE FROM title WHERE id={0}".format(m['id']))

	def _add_res_to_dict(self, col_names, res, d):
		for k, v in zip(col_names, res):
			if v != None:
				if k in self.type_map and v in self.type_map[k][1]:
					v = self.type_map[k][1][v]
					k = self.type_map[k][0]
				d[k] = v
		return d
		
	def clean(self):
		pass
		
def has_person(m, persons, role):		
	if len(persons) == 0:
		return True
	for d1 in m[role]:
		for d2 in persons:
			if d1['name'] == d2:
				return True
	return False
	
def clean_unicode_errors(data):
	if isinstance(data, dict):
		for k, v in data.items():
			data[clean_unicode_errors(k)] = clean_unicode_errors(data[k])
	elif isinstance(data, list):
		for i, v in enumerate(data):
			data[i] = clean_unicode_errors(v)
	elif isinstance(data, str):
		try:
			data.decode("utf8")
		except UnicodeDecodeError:
			return "Unicode Decode Error"
	return data
			
if __name__ == '__main__':
	a = IMDBInterface()
