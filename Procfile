web: python tunnel.py && gunicorn leaderboard.wsgi --log-file -
worker: python tunnel.py && python dblistener.py
