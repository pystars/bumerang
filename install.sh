#!/bin/bash -x
add-apt-repository -y ppa:shiki/mediainfo
add-apt-repository -y ppa:stebbins/handbrake-snapshots
echo """
deb http://eu-west-1.ec2.archive.ubuntu.com/ubuntu/ oneiric multiverse
deb-src http://eu-west-1.ec2.archive.ubuntu.com/ubuntu/ oneiric multiverse
deb http://eu-west-1.ec2.archive.ubuntu.com/ubuntu/ oneiric-updates multiverse
deb-src http://eu-west-1.ec2.archive.ubuntu.com/ubuntu/ oneiric-updates multiverse
""" >> /etc/apt/sources.list
apt-get update
apt-get upgrade -y
apt-get install -y gcc g++ python-dev libxml2-dev libpq-dev mercurial git \
subversion virtualenvwrapper nginx yasm build-essential autoconf libtool\
 libbz2-dev libfribidi-dev intltool libglib2.0-dev libdbus-glib-1-dev\
  libgtk2.0-dev libgudev-1.0-dev libwebkit-dev libnotify-dev\
   libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev checkinstall \
    libfaac-dev libjack-jackd2-dev libmp3lame-dev libopencore-amrnb-dev\
     libopencore-amrwb-dev libsdl1.2-dev libtheora-dev libva-dev libvdpau-dev \
     libvorbis-dev libx11-dev libxfixes-dev texi2html libmysqlclient-dev \
     libjpeg62-dev
apt-get remove ffmpeg x264 libx264-dev
cd /opt
git clone git://git.videolan.org/x264
cd x264
./configure --enable-static
make
checkinstall --pkgname=x264 --pkgversion="3:$(./version.sh | awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes --fstrans=no --default
apt-get remove libvpx-dev
cd /opt
git clone http://git.chromium.org/webm/libvpx.git
cd libvpx
./configure
make
sudo checkinstall --pkgname=libvpx --pkgversion="1:$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default
cd /opt
git clone --depth 1 git://source.ffmpeg.org/ffmpeg
cd ffmpeg
./configure --enable-gpl --enable-libfaac --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-nonfree --enable-version3 --enable-x11grab --enable-libvpx
make
checkinstall --pkgname=ffmpeg --pkgversion="5:$(date +%Y%m%d%H%M)-git" --backup=no --deldoc=yes --fstrans=no --default
hash x264 ffmpeg ffplay ffprobe
apt-get install handbrake-cli
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
chown -R www-data:adm /home/ubuntu/bumerang
# on web we need add this
ln -s /home/ubuntu/bumerang/nginx.conf /etc/nginx/sites-enabled/bumerang.conf
service nginx restart
uwsgi --ini /home/ubuntu/bumerang/uwsgi.ini
# on converter we need add this
ln -s /home/ubuntu/bumerang/celery.sh /etc/init.d/celeryd
ln -s /home/ubuntu/bumerang/celeryd.cnf /etc/default/celeryd