import json
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from gripcontrol import HttpStreamFormat
from django_grip import set_hold_stream, publish
from .models import ObjectDoesNotExist, Board, Player

def _board_data(board, players):
	return {'players': [_player_data(p) for p in players]}

def _board_json(board, players, pretty=True):
	if pretty:
		indent = 4
	else:
		indent = None
	return json.dumps(_board_data(board, players), indent=indent)

def _board_response(board, players):
	return HttpResponse(_board_json(board, players) + '\n', content_type='application/json')

def _player_data(player):
	return {'id': player.id, 'name': player.name, 'score': player.score}

def _player_json(player):
	return json.dumps(_player_data(player), indent=4)

def _player_response(player):
	return HttpResponse(_player_json(player) + '\n', content_type='application/json')

def board(request, board_id):
	if request.method == 'GET':
		try:
			board = Board.get(board_id)
		except ObjectDoesNotExist:
			return HttpResponseNotFound('Not Found\n')

		accept = request.META['HTTP_ACCEPT']
		if accept:
			accept = accept.split(',')[0].strip()
		if accept == 'text/event-stream':
			set_hold_stream(request, str(board_id))
			return HttpResponse(content_type='text/event-stream')
		else:
			players = Player.get_top_for_board(board, limit=5)
			return _board_response(board, players)
	else:
		return HttpResponseNotAllowed(['GET'])

def board_player(request, board_id, player_id):
	if request.method == 'GET':
		try:
			player = Player.get_for_board(Board(id=board_id), player_id)
		except ObjectDoesNotExist:
			return HttpResponseNotFound('Not Found\n')

		return _player_response(player)
	else:
		return HttpResponseNotAllowed(['GET'])

def board_player_score_add(request, board_id, player_id):
	if request.method == 'POST':
		try:
			player = Player.get_for_board(Board(id=board_id), player_id)
		except ObjectDoesNotExist:
			return HttpResponseNotFound('Not Found\n')

		player.score_add(1)
		return _player_response(player)
	else:
		return HttpResponseNotAllowed(['POST'])

def publish_board(board):
	players = Player.get_top_for_board(board, limit=5)
	publish(str(board.id), HttpStreamFormat('event: update\ndata: %s\n\n' % _board_json(board, players, pretty=False)))
