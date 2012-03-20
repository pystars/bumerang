#!/bin/bash -x
apt-get update
apt-get upgrade -y
apt-get install gcc g++ python-dev libxml2-dev libpq-dev mercurial git-core subversion virtualenvwrapper nginx -y
pip install uwsgi
git clone git://github.com/pystars/bumerang.git /home/ubuntu/bumerang
mkdir /var/www
mkdir /var/log/uwsgi
mkdir /var/run/uwsgi
virtualenv --no-site-packages --unzip-setuptools /var/www/.virtualenvs/bumerang
pip -E /var/www/.virtualenvs/bumerang install -U -r /home/ubuntu/bumerang/requirements.txt
chown -R www-data:adm /var/www
chown -R www-data:adm /var/log/uwsgi
chmod -R 750 /var/log/uwsgi
chown -R www-data:adm /var/run/uwsgi
chmod -R 750 /var/run/uwsgi
chown -R ubuntu:ubuntu /home/ubuntu/baltoapi
ln -s /home/ubuntu/bumerang/nginx.conf /etc/nginx/sites-enabled/bumerang.conf