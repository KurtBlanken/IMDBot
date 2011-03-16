'''
Created on Mar 12, 2011

@author: gabrielsanchez

'''
import MySQLdb
import re;

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
		
		cur.execute("show tables")
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
		cur.close()
		
		self.cur = conn.cursor(MySQLdb.cursors.DictCursor)
		self.tables = tables
		self.type_map = type_map
		self.info_type_id = {}
		for key, value in self.type_map['info_type_id'][1].items():
			self.info_type_id[key] = value
		
		self.movie_cache = {}
		self.person_cache = {}
	
	
	
	'''
	@param id: id of the movie
	@param movie_info: Specifies whether the returned dictionary should contain movie information (True by default)
	@param info_keys: List of types of information to return in the dictionary
	@param cast_info: Specifies whether the returned dictionary should contain cast information. (True by default)
	
	The returned dictionary contains the keys:
		id: Index of movie in database
		title: Title of movie
		production_year: Year of production
		cast_info lists: actresses, actors, directors, composers, producers, writers. Each list contains dictionaries
			with keys: id, formal_name, and name.
		movie_info lists: one for each info_type.
	'''	
	def get_movie(self, id, movie_info=True, info_keys="*", cast_info=True):
		if id in self.movie_cache:
			return self.movie_cache[id]
		self.cur.execute("SELECT * FROM title WHERE id= {0} AND kind_id= 1".format(id))
		result= self.cur.fetchall()
		if len(result) < 1:
			return None
		result= result[0]
		if movie_info:
			query = 'SELECT * FROM movie_info WHERE movie_id={0}'.format(id)
			if info_keys != "*":
				info_keys = ', '.join([str(self.info_type_id[key]) for key in info_keys])
				query += ' AND info_type_id IN ({0})'.format(info_keys)
			self.cur.execute(query)
			rows = self.cur.fetchall()
			for row in rows:
				info_type= self.info_type_id[row['info_type_id']]
				if info_type not in result:
					result[info_type]= []
				result[info_type].append(row['info'])
		if cast_info:
			types= ['actor', 'actress', 'director', 'writer', 'composer', 'producer']
			for index, role in self.type_map['role_id'][1].items():
				if role in types:
					if role == 'actress':
						role= 'actresses'
					else:
						role= role+'s'
					
					result[role]= []
					self.cur.execute('SELECT * FROM cast_info WHERE movie_id={0} AND role_id={1}'.format(id, index))
					rows= self.cur.fetchall()
					#print rows
					if len(rows) > 0:
						# Extract names and ids
						for row in rows:
							person_id= row['person_id']
							self.cur.execute("SELECT name FROM name WHERE id= {0}".format(person_id))
							names= self.cur.fetchall()
							name= names[0]['name']
							

							# Dictionaries are non-hashable
							dict= {}
							dict['formal_name']= name
							dict['id']= person_id
							
							if len(re.split(r',\s+', name)) > 1:
								tokens= [token.strip() for token in re.split(r',\s+', name)]
								tokens.reverse()
								dict['name']= ' '.join(tokens)
								
							
							result[role].append(dict)
							
						#result[role].sort(key=(lambda x: x['name']))	
							
		
		self.movie_cache[id]= result
		
		#print result
		return result
		
	'''
	@param id: id of the person
	The returned dictionary contains the keys:
		id: Index of person in the database
		name: First Last
		formal_name: Last, First
		movies: Set of tuples (movie_id, title, role_type) 
	'''	
		
	def get_person(self, id):
		if id in self.person_cache:
			return self.person_cache[id]
		self.cur.execute("SELECT * FROM name WHERE id= {0}".format(id))
		result= self.cur.fetchall()
		#print result
		if len(result) < 1:
			return None
		result = result[0]
		# This set will contain a tuple of (role, movie_id, title)
		result["movies"]= set()
		result['formal_name']= result['name']
		
		if len(result['formal_name'].split(",")) > 1:
			names = [name.strip() for name in result['formal_name'].split(",")]
			names.reverse()
			result['name'] = ' '.join(names)
		
		
		self.cur.execute("SELECT * From cast_info WHERE person_id= {0}".format(id))
		for row in self.cur.fetchall():
			role= self.type_map["role_id"][1][row["role_id"]]
			movie_id= row["movie_id"]
			
			# Get movie title
			self.cur.execute("SELECT title FROM title WHERE id={0}".format(movie_id))
			rows= self.cur.fetchall()
			rows= rows[0]
			title= rows["title"]
			
			result["movies"].add((movie_id, title, role))
		
		self.person_cache[id]= result
		
		#print result
		return result
		
if __name__ == "__main__":
	import time
	start= time.time()
	imdbi= IMDBInterface()
	imdbi.get_person(76010)
	imdbi.get_movie(595948)
	end= time.time()
	
	print end - start