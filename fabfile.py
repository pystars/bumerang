from fabric.api import *
from fabric.context_managers import lcd, hide, cd
from fabric.operations import local, abort, put, sudo

from local_settings import get_sudo_pwd

#__all__ = ['test']
env.hosts = [u"web@62.76.179.205:22"]
env.passwords = { u"web@62.76.179.205:22" : get_sudo_pwd() } 

def sync():
	put('./bumerang.db', '/web/bumerang/')
	sudo('supervisorctl restart bumerang')
	sudo('service nginx restart')

def update():
	with cd('/web/bumerang'):
		run('workon bumerang')
		run('git stash save')
		run('git pull origin dev')
		run('git stash pop')
