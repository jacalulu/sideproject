from fabric.api import run
from fabric.api import env
from fabric.api import cd

env.hosts = [
 '162.144.59.13'
 ]

def deploy():
 with cd('/var/srv/sideproject'):
 	run('git pull')
 	run('npm install')
 	run('forever app.js')