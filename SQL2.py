
import MySQLdb
import nltk
import os,sys
import random

class IMDBSQL:
    def __init__(self):

        dbinfo = eval(open('dbinfo.txt').read())
        try:
            self.conn = MySQLdb.connect(host=dbinfo['host'],
                                   user=dbinfo['user'],
                               passwd=dbinfo['passwd'],
                                      db=dbinfo['db']) 
        except MySQLdb.Error, e:
            print 'Error %d: %s' % (e.args[0], e.args[1])
            self.conn= None

    def __del__(self):
        self.conn.close()

    def findMovie(self, text, limit):
        if self.conn != None:
            tokens= nltk.word_tokenize(text)
            query= '_'.join(tokens)
            query+='%'
            print query
            cursor= self.conn.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM title WHERE title LIKE '%s' ORDER BY\
                           production_year DESC LIMIT %d" % (query,limit))
            rows= cursor.fetchall()
            cursor.close()
            return rows

    def findPerson(self, text, limit):
        if self.conn != None:
            tokens= nltk.word_tokenize(text)
            if len(tokens) == 2:
                query= '%'.join(tokens[::-1])
                print query
                cursor= self.conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute("SELECT * FROM name WHERE name LIKE '%s' ORDER\
                               BY imdb_index ASC LIMIT %d" % (query, limit))
                rows= cursor.fetchall()
                cursor.close()
                return rows

    def getPeople(self,limit):
        if self.conn != None:
            cursor= self.conn.cursor()
            # Need to generate random ids since MySQL RAND() too slow
            cursor.execute("SELECT MAX(id) AS max_id FROM cast_info")
            max_id= cursor.fetchone()
            max_id= max_id[0]
            
            id_list= random.sample(xrange(1,max_id),limit)

            #print id_list

            # First get all actors/actresses from cast_info
            #cursor.execute("SELECT person_id FROM cast_info WHERE role_id=1\
            #              OR role_id=3 LIMIT %d" % limit)
            cursor.execute("SELECT person_id FROM cast_info WHERE id IN (%s)\
                           AND (role_id=1 OR role_id=3)" %
                           ','.join(["%s" % id for id in id_list]))


            rows= cursor.fetchall()
            rows= set(rows)
            # Collapse every person_id so that there are no duplicates
            rows= [row[0] for row in rows]
            # Extract actor/actress name
            actors=[]
            for id in rows:
                cursor.execute("SELECT name FROM name WHERE id=%d" % id)
                name= cursor.fetchone()
                actors.append(name[0])
            cursor.close()

            return actors
    
    def getMovies(self, limit):
        if self.conn != None:
            cursor= self.conn.cursor()
            # Generate random ids
            cursor.execute("SELECT MAX(id) AS max_id FROM title")
            max_id= cursor.fetchone();
            max_id= max_id[0]

            id_list= random.sample(xrange(1,max_id),limit)


            cursor.execute ("SELECT title FROM title WHERE id IN (%s) AND\
                            kind_id= 1 LIMIT %d" % (','.join(["%s" % id for id in
                                                            id_list]),limit))

            rows= cursor.fetchall()
            rows= [row[0] for row in rows]
            cursor.close()
            
            return rows
