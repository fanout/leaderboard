import os
import time
import traceback
import logging
import django
from rethinkdb.errors import RqlDriverError
from leaderboardapp.models import Board, Player
from leaderboardapp.views import publish_board

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leaderboard.settings')
django.setup()

logger = logging.getLogger('dblistener')

while True:
	try:
		for change in Player.get_all_changes():
			logger.debug('got change: %s' % change)
			try:
				row = change['new_val']
				board = Board.get(row['board'])
				publish_board(board)
			except Exception as e:
				logger.debug('failed to handle', e)
	except RqlDriverError:
		time.sleep(1)
