from fabric.api import *
from fabric.context_managers import lcd, hide, cd
from fabric.operations import local, abort, put, sudo

from bumerang.local_settings import get_sudo_pwd

#__all__ = ['test']
env.hosts = [u"web@62.76.179.205:22"]
env.passwords = { u"web@62.76.179.205:22" : get_sudo_pwd() } 

def syncdb():
	'''
	Makes local syncdb and load fixtures
	'''
	local('python ./manage.py reset_db --noinput --router=default')
	local('python ./manage.py syncdb --noinput --migrate')
	local('python ./manage.py loaddata fixtures/*.json')

def makemedia():
    '''
    Makes media direcory structure
    '''
    local('mkdir ./bumerang/media/tmp')
    local('mkdir ./bumerang/media/uploads')
    local('mkdir ./bumerang/media/prewiews')
    local('mkdir ./bumerang/media/prewiews/video')
    local('mkdir ./bumerang/media/prewiews/video-album')
    local('mkdir ./bumerang/media/teachers')
    local('mkdir ./bumerang/media/teams')
    local('mkdir ./bumerang/media/videos')

def collectstatic():
    run('/home/web/.virtualenvs/bumerang/bin/python /web/bumerang/manage.py collectstatic  -l --traceback --noinput')

def remote_syncdb():
    '''
	Makes remote syncdb and load fixtures
	'''
    with cd('/web/bumerang'):
        run('/home/web/.virtualenvs/bumerang/bin/python ./manage.py reset_db --noinput --router=default')
        run('/home/web/.virtualenvs/bumerang/bin/python ./manage.py syncdb --noinput --migrate')
        run('/home/web/.virtualenvs/bumerang/bin/python ./manage.py loaddata fixtures/*.json')

def celeryd():
    '''
    Runs celeryd process on local machine
    '''
    local('python ./manage.py celeryd -v 0')

def update(branch):
	'''
	 Makes git pull
	'''
	with cd('/web/bumerang'):
		run('git reset --hard HEAD')
		run('git pull origin {0}'.format(branch))

#def sync():
#	put('./bumerang.db', '/web/bumerang/')

def reload():
    sudo('supervisorctl restart bumerang')
    sudo('supervisorctl restart bumerang_celeryd')
    sudo('service nginx restart')

def fullsync(branch):
	update(branch)
	#sync()
	remote_syncdb()
	reload()
	

# def getvideo():
# 	with cd('/web/bumerang'):
# 		get('/web/videoconverting-tester/media/converted/1-B64-w720-ZHigh_Profile-b900-r25.mp4', './')
