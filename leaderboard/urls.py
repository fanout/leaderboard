from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'leaderboard.views.home', name='home'),
    url(r'^boards/', include('leaderboardapp.urls')),
    url(r'^admin/', include(admin.site.urls))
]
