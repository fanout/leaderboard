import os
import sys
import subprocess

key_file = 'tunnel.pem'

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

try:
	pid = int(subprocess.check_output(['pgrep', '-f', cmd]))
	print 'SSH tunnel already running. PID=%d' % pid
	sys.exit(0)
except subprocess.CalledProcessError:
	# not running
	pass

f = open(key_file, 'w')
f.write(out)
f.close()

os.chmod(key_file, 0600)

print 'Starting SSH tunnel: %s' % cmd

try:
	subprocess.check_call(args)
finally:
	os.remove(key_file)
