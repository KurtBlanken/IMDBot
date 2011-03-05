import MySQLdb
import os, sys
from collections import defaultdict

class IMDBInterface(object):
	def __init__(self):
		dbinfo = eval(open('dbinfo.txt').read())

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
		
		self.cur = cur
		self.tables = tables
		self.type_map = type_map
		self.info_type_id = {}
		for key, value in self.type_map['info_type_id'][1].items():
			self.info_type_id[value] = key

	def get_movie(self, id, movie_info=True, info_keys="*", cast_info=True):
		self.cur.execute('SELECT * FROM title WHERE id={0}'.format(id))
		res = self.cur.fetchall()
		assert len(res) == 1
		res = res[0]
		d = defaultdict(list)
		self._add_res_to_dict(self.tables['title'], res, d)
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
			d['actors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actor', d['cast'])
			d['actresses'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'actress', d['cast'])
			d['writers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'writer', d['cast'])
			d['directors'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'director', d['cast'])
			d['producers'] = filter(lambda i: 'role_type' in i and i['role_type'] == 'producer', d['cast'])
		return d
	
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
	
	def get_person(self, id):
		self.cur.execute('SELECT * FROM name WHERE id={0}'.format(id))
		res = self.cur.fetchall()
		assert len(res) == 1
		res = res[0]
		d = {}
		self._add_res_to_dict(self.tables['name'], res, d)
		self.cur.execute('SELECT * FROM cast_info WHERE person_id={0}'.format(id))
		res = self.cur.fetchall()
		for r in res:
			d2 = {}
			self._add_res_to_dict(self.tables['cast_info'], r, d2)
			if 'role_type' in d2:
				if d2['role_type'] not in d:
					d[d2['role_type']] = set()
				d[d2['role_type']].add(d2['movie_id'])
		return d
		
	def get_movie_ids(self):
		self.cur.execute('SELECT id FROM title'.format(id))
		return map(lambda row: row[0], self.cur.fetchall())

	def _add_res_to_dict(self, col_names, res, d):
		for k, v in zip(col_names, res):
			if v != None:
				if k in self.type_map and v in self.type_map[k][1]:
					v = self.type_map[k][1][v]
					k = self.type_map[k][0]
				d[k] = v
		return d
			
if __name__ == '__main__':
	imdb = IMDBInterface()
	ids = [line.split()[0] for line in open("title_index.txt").readlines()]
	store = {}
	for id in ids:
	  store[id] = imdb.get_movie(id)
	import cPickle
	cPickle.dump(store, "title_db.txt")
	#ids = imdb.get_movie_ids()
	#for i, id in enumerate(ids):
		#print i / float(len(ids))
		#m = imdb.get_movie(id, info_keys=['genres'], cast_info=False)
		#print m['genres']
