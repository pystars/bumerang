from time import sleep

from fabric.api import *
from fabric.context_managers import lcd, hide, cd
from fabric.operations import local, abort, put, sudo
from boto.ec2 import connect_to_region

from bumerang.local_settings import (get_sudo_pwd, AWS_ACCESS_KEY_ID,
                                     AWS_SECRET_ACCESS_KEY)

#__all__ = ['test']
#env.hosts = [u"web@62.76.179.205:22"]
#env.passwords = { u"web@62.76.179.205:22" : get_sudo_pwd() }

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
    local('mkdir ./bumerang/media/photos')

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

env.key_filename = '/Users/goodfellow/.ssh/eu-bumerang'
ami_instance = 'ami-af5069db'

def create_instance(connection, server_type):
    print 'start creating instance'
    if server_type=='converter':
        instance_type = 'c1.medium'
    elif server_type=='streamer':
        instance_type = 'm1.medium'
    else:
        instance_type = 'm1.medium'
    security_groups = ['bumerang-{0}'.format(server_type)]
    reservation = connection.run_instances(ami_instance,
        key_name='pystars-keypair', security_groups=security_groups,
        instance_type=instance_type, placement='eu-west-1c')
    print 'created reservation ', reservation
    instance = reservation.instances[0]
    while not instance.dns_name:
        sleep(1)
        instance.update()
    print 'instance runned, dns is {0}'.format(instance.dns_name)
    print 'wait while ssh is up... about 15 seconds'
    sleep(15)
    env.host_string = 'ubuntu@{0}:22'.format(instance.dns_name)
    for line in open('install_{0}.sh'.format(server_type)):
        if not line.startswith('#'):
            sudo(line)
    return instance

def create_web():
    connection = connect_to_region('eu-west-1',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    instance = create_instance(connection, 'web')
    print 'creating image from instance {0}'.format(instance)
#    image_id = connection.create_image(instance.id, 'testimage')
#    print 'image {0} created'.format(image_id)




# def getvideo():
# 	with cd('/web/bumerang'):
# 		get('/web/videoconverting-tester/media/converted/1-B64-w720-ZHigh_Profile-b900-r25.mp4', './')
