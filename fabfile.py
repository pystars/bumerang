from fabric.api import *
from fabric.context_managers import lcd, hide, cd
from fabric.operations import local, abort, put, sudo

from local_settings import get_sudo_pwd

#__all__ = ['test']
env.hosts = [u"web@62.76.179.205:22"]
env.passwords = { u"web@62.76.179.205:22" : get_sudo_pwd() } 

def update(branch):
	'''
	 Makes git pull
	'''
	with cd('/web/bumerang'):
		run('git reset --hard HEAD')
		run('git pull origin {0}'.format(branch))

def sync():
	put('./bumerang.db', '/web/bumerang/')

def reload():
	sudo('supervisorctl restart bumerang')
	sudo('service nginx restart')

def fullsync(branch):
	update(branch)
	sync()
	reload()
	

# def getvideo():
# 	with cd('/web/bumerang'):
# 		get('/web/videoconverting-tester/media/converted/1-B64-w720-ZHigh_Profile-b900-r25.mp4', './')
