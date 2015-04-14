# SSH tunnel script
#
# Set the following environment variables:
#
#   SSH_TUNNEL_TARGET=user@hostname:port
#   SSH_TUNNEL_KEY=RSA:{base64 private key}
#   SSH_TUNNEL_FORWARDS=localaddr:localport:remoteaddr:remoteport,[...]
#
# Notes:
#
#   SSH_TUNNEL_KEY is the key type (e.g. "RSA"), a colon character, and then
#   the ssh private key in base64 without the headers/footers or newlines.
#   Yes, you're setting an entire giant ssh key as an environment variable,
#   but it works. :)
#
#   SSH_TUNNEL_FORWARDS is a comma-separated list of args that would normally
#   each be preceded by -L in an ssh command.
#
# In your Procfile, simply run the tunnel before any workers that need it.
#
#   web: python tunnel.py && ....
#
# It's safe to run the script multiple times concurrently. Only one tunnel will
# be made and the other invocations will fail successfully. This way multiple
# workers can depend on the tunnel, and you can still use foreman locally.
#
import os
import sys
from tempfile import NamedTemporaryFile
import subprocess

def check_already_running(forwards):
	try:
		lines = subprocess.check_output(['pgrep', '-x', '-a', 'ssh']).split('\n')
	except subprocess.CalledProcessError:
		lines = list()

	for line in lines:
		if not line:
			continue
		pid, cmd = line.split(' ', 1)
		pid = int(pid)
		found = False
		for f in forwards:
			if f in cmd:
				found = True
				break
		if found:
			print 'SSH tunnel already running. PID=%d' % pid
			return True
	return False

target = os.environ['SSH_TUNNEL_TARGET']
at = target.find(':')
if at != -1:
	port = int(target[at + 1:])
	target = target[:at]
else:
	port = None

key = os.environ['SSH_TUNNEL_KEY']

forwards = os.environ['SSH_TUNNEL_FORWARDS'].split(',')

type, blob = key.split(':', 1)

out = '-----BEGIN %s PRIVATE KEY-----\n' % type
for n in range(0, ((len(blob) - 1) / 64) + 1):
	out += blob[n*64:(n*64)+64] + '\n'
out += '-----END %s PRIVATE KEY-----\n' % type

f = NamedTemporaryFile(delete=False)
key_file = f.name

try:
	f.write(out)
	f.close()

	args = [
		'ssh',
		'-f',
		'-N',
		'-i', key_file,
		'-o', 'StrictHostKeyChecking=no',
		'-o', 'ExitOnForwardFailure=yes'
	]

	for f in forwards:
		args.extend(['-L', f])

	if port is not None:
		args.extend(['-p', str(port)])

	args.append(target)

	cmd = ' '.join(args)

	if check_already_running(forwards):
		sys.exit(0)

	print 'Starting SSH tunnel: %s' % cmd

	try:
		subprocess.check_call(args)
	except subprocess.CalledProcessError:
		if not check_already_running(forwards):
			raise
finally:
	os.remove(key_file)
