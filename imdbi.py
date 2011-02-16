import MySQLdb
import os, sys

class IMDBInterface(object):
	def __init__(self):
		dbinfo = eval(open('dbinfo.txt').read())

		try:
			conn = MySQLdb.connect(host='127.0.0.1',
														 user=dbinfo['user'],
														 passwd=dbinfo['passwd'],
														 db=dbinfo['db'],
														 connect_timeout=2)
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
		
		self.cur = cur
		self.tables = tables
		self.type_map = type_map

	def get_movie(self, id):
		self.cur.execute('SELECT * FROM title WHERE id={0}'.format(id))
		res = self.cur.fetchall()
		assert len(res) == 1
		res = res[0]
		d = {}
		self._add_res_to_dict(self.tables['title'], res, d)
		self.cur.execute('SELECT * FROM movie_info WHERE movie_id={0}'.format(d['id']))
		res = self.cur.fetchall()
		for r in res:
			d2 = {}
			self._add_res_to_dict(self.tables['movie_info'], r, d2)
			if d2['info_type'] not in d:
				d[d2['info_type']] = []
			d[d2['info_type']].append(d2['info'])
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
		pass

	def _add_res_to_dict(self, col_names, res, d):
		for k, v in zip(col_names, res):
			if v != None:
				if k in self.type_map and v in self.type_map[k][1]:
					v = self.type_map[k][1][v]
					k = self.type_map[k][0]
				d[k] = v
		return d
