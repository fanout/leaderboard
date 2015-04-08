from django.conf import settings
from django.shortcuts import render
from leaderboardapp.models import Board, Player

def home(request):
	board = Board.get_one()
	players = Player.get_top_for_board(board)
	api_base_uri = '/boards/%s' % board.id
	if hasattr(settings, 'LEADERBOARD_API_HOST'):
		api_base_uri = 'http://' + settings.LEADERBOARD_API_HOST + api_base_uri
	context = {
		'api_base_uri': api_base_uri,
		'players': players
	}
	return render(request, 'leaderboard/home.html', context)
