from time import sleep

from fabric.api import *
from fabric.context_managers import lcd, hide, cd
from fabric.operations import local, abort, put, sudo
from boto.ec2 import connect_to_region

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
    local('mkdir ./bumerang/media/previews')
    local('mkdir ./bumerang/media/previews/video')
    local('mkdir ./bumerang/media/previews/video-album')
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


env.key_filename = '/home/goodfellow/.ssh/dev_amazon_eu.pub'

def create_instance(connection):
    print 'start creating instance'
    reservation = connection.run_instances('ami-895069fd',
        key_name='devkeypair', security_groups=['dev api'],
        instance_type='c1.xlarge')
    print 'created reservation ', reservation
    instance = reservation.instances[0]
    while not instance.dns_name:
        sleep(1)
        instance.update()
    print 'instance runned, dns is {0}'.format(instance.dns_name)
    print 'wait while ssh is up... about 15 seconds'
    sleep(15)
    env.host_string = 'ubuntu@{0}:22'.format(instance.dns_name)
    for line in open('install.sh'):
        if not line.startswith('#'):
            sudo(line)
    return instance

def create_image():
    connection = connect_to_region('eu-west-1')
    instance = create_instance(connection)
    print 'creating image from instance {0}'.format(instance)
    image_id = connection.create_image(instance.id, 'testimage')
    print 'image {0} created'.format(image_id)




# def getvideo():
# 	with cd('/web/bumerang'):
# 		get('/web/videoconverting-tester/media/converted/1-B64-w720-ZHigh_Profile-b900-r25.mp4', './')
