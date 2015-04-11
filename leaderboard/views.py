from django.conf import settings
from django.shortcuts import render
from leaderboardapp.models import Board, Player

def home(request):
	board = Board.get_one()
	players = Player.get_top_for_board(board)
	board_uri = '%s/boards/%s' % (settings.LEADERBOARD_API_BASE, board.id)
	context = {
		'board_uri': board_uri,
		'players': players
	}
	return render(request, 'leaderboard/home.html', context)
