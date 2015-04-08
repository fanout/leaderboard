from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<board_id>[^/]+)/$', views.board, name='board'),
    url(r'^(?P<board_id>[^/]+)/players/(?P<player_id>[^/]+)/$', views.board_player, name='board_player'),
    url(r'^(?P<board_id>[^/]+)/players/(?P<player_id>[^/]+)/score-add/$', views.board_player_score_add, name='board_player_score_add'),
]
