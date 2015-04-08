from django.shortcuts import render
from leaderboardapp.models import Board, Player

def home(request):
	board = Board.get_one()
	players = Player.get_top_for_board(board)
	context = {
		'api_base_uri': 'http://localhost:7999/boards/%s' % board.id,
		'players': players
	}
	return render(request, 'leaderboard/home.html', context)
