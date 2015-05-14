import os
from urlparse import urlparse
import threading
import rethinkdb as r

_threadlocal = threading.local()

_url_parsed = urlparse(os.environ['DATABASE_URL'])
assert(_url_parsed.scheme == 'rethinkdb')
hostname = _url_parsed.hostname
port = _url_parsed.port
dbname = _url_parsed.path[1:]
del _url_parsed

def _ensure_db(conn):
	# create database
	try:
		r.db_create(dbname).run(conn)

		# some defaults
		board = Board()
		board.save()
		Player(board=board, name='TS').save()
		Player(board=board, name='Brodie').save()
		Player(board=board, name='Brandi').save()
		Player(board=board, name='Rene').save()
		Player(board=board, name='Stan').save()
	except r.RqlRuntimeError:
		# already created
		pass

def _get_conn():
	if not hasattr(_threadlocal, 'conn'):
		_threadlocal.conn = r.connect(hostname, port)
		_ensure_db(_threadlocal.conn)
	return _threadlocal.conn

class ObjectDoesNotExist(object):
	pass

class Board(object):
	def __init__(self, id=None):
		self.id = id

	def save(self):
		if self.id:
			# nothing to update
			pass
		else:
			ret = Board.get_table().insert({}).run(_get_conn())
			self.id = ret['generated_keys'][0]

	def reload(self):
		# nothing to load
		pass

	def delete(self):
		assert(self.id)
		self.get_table().filter({'board': self.id}).delete().run(_get_conn())
		self.get_row().delete().run(_get_conn())

	def get_row(self):
		assert(self.id)
		return Board.get_table().get(self.id)

	def __repr__(self):
		return u'<%s: %s>' % (type(self).__name__, self.__unicode__())

	def __unicode__(self):
		return u'%s' % (self.id)

	@staticmethod
	def get_table():
		try:
			r.db(dbname).table_create('boards').run(_get_conn())
		except r.RqlRuntimeError:
			# already created
			pass
		return r.db(dbname).table('boards')

	@staticmethod
	def get_all():
		out = list()
		for row in Board.get_table().run(_get_conn()):
			out.append(Board(id=row['id']))
		return out

	@staticmethod
	def get(id=None):
		row = Board.get_table().get(id).run(_get_conn())
		if row is None:
			raise ObjectDoesNotExist()
		return Board(id=row['id'])

	@staticmethod
	def get_one():
		ret = list(Board.get_table().limit(1).run(_get_conn()))
		if len(ret) < 1:
			raise ObjectDoesNotExist()
		return Board(id=ret[0]['id'])

class Player(object):
	def __init__(self, id=None, board=None, name=None, score=None):
		self.id = id
		self.board = board
		if name is not None:
			self.name = name
		else:
			self.name = ''
		if score is not None:
			self.score = score
		else:
			self.score = 0

	def save(self):
		if self.id:
			self.get_row().update({
				'name': self.name,
				'score': self.score,
			}).run(_get_conn())
		else:
			assert(self.board)
			ret = Player.get_table().insert({
				'name': self.name,
				'score': self.score,
				'board': self.board.id
			}).run(_get_conn())
			self.id = ret['generated_keys'][0]

	def reload(self):
		self.apply_rowdata(self.get_row().run(_get_conn()))

	def delete(self):
		self.get_row().delete().run(_get_conn())

	def score_add(self, amount):
		self.get_row().update({
			'score': r.row['score'].add(amount)
		}).run(_get_conn())
		self.reload()

	def get_row(self):
		assert(self.id)
		return Player.get_table().get(self.id)

	def apply_rowdata(self, row):
		if not self.id:
			self.id = row['id']
		if self.board is None:
			self.board = Board(id=row['board'])
		self.name = row['name']
		self.score = row['score']

	def __repr__(self):
		return u'<%s: %s>' % (type(self).__name__, self.__unicode__())

	def __unicode__(self):
		return u'%s, %s, %s' % (self.id, self.name, self.score)

	@staticmethod
	def get_table():
		try:
			r.db(dbname).table_create('players').run(_get_conn())
		except r.RqlRuntimeError:
			# already created
			pass
		return r.db(dbname).table('players')

	@staticmethod
	def get_all():
		out = list()
		for row in Player.get_table().run(_get_conn()):
			p = Player()
			p.apply_rowdata(row)
			out.append(p)
		return out

	@staticmethod
	def get(id):
		row = Player.get_table().get(id).run(_get_conn())
		if row is None:
			raise ObjectDoesNotExist()
		p = Player()
		p.apply_rowdata(row)
		return p

	@staticmethod
	def get_all_for_board(board):
		out = list()
		for row in Player.get_table().filter({'board': board.id}).run(_get_conn()):
			p = Player(board=board)
			p.apply_rowdata(row)
			out.append(p)
		return out

	@staticmethod
	def get_top_for_board(board, limit=10):
		out = list()
		rows = Player.get_table().\
			order_by(r.desc('score')).\
			filter({'board': board.id}).\
			limit(limit).run(_get_conn())
		for row in rows:
			p = Player(board=board)
			p.apply_rowdata(row)
			out.append(p)
		return out

	@staticmethod
	def get_for_board(board, id):
		row = Player.get_table().get(id).run(_get_conn())
		if row is None or row['board'] != board.id:
			raise ObjectDoesNotExist()
		p = Player(board=board)
		p.apply_rowdata(row)
		return p

	@staticmethod
	def get_all_changes():
		# use dedicated connection
		changes_conn = r.connect(hostname, port)
		return Player.get_table().changes().run(changes_conn)
