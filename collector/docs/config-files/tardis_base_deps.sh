#! /bin/bash

echo `hostname`

yum list installed | grep epel

echo "EPEL should be installed..."

sudo yum install git-core ncurses-devel tree
sudo yum install mysql.x86_64 mysql-server.x86_64 mysql-devel.x86_64

sudo yum install python26.x86_64 python26-devel.x86_64
sudo yum install python26-mod_wsgi.x86_64

pushd /tmp
curl -O http://python-distribute.org/distribute_setup.py
sudo python26 distribute_setup.py
popd

which easy_install-2.6

echo "... doing an easy-install of 'pip'"

sudo easy_install-2.6 pip

git clone https://github.com/iPlantCollaborativeOpenSource/tardis-apis

pushd tardis-apis/collector/
sudo pip-2.6 install -r requirements.txt
popd

pushd /opt/
sudo mkdir -p tardis/collector
sudo chown -R apache:staff tardis

ls -lha | grep tardis

sudo chmod -R g+w tardis
popd

echo "... creating symlink to scripts target home"

sudo ln -s /opt/tardis/collector/ /scripts
sudo chown apache:staff /scripts/
sudo chmod -R g+w /scripts/

pushd tardis-apis/collector/
cp src/*.py /scripts/

ls -lha /scripts/
popd

echo "... create a directory WSGI socket files"
sudo mkdir /opt/wsgi/
sudo chown -R apache:apache /opt/wsgi
ls -lha /opt/wsgi

echo "... create logging files and structure"

pushd /var/log
sudo mkdir tardis
sudo chown -R apache:staff tardis/

pushd tardis/
mkdir audit
mkdir history
touch provenance.log
touch Object-lookup.log
touch audit/object_failed_inserts.txt
touch audit/prov_failed_inserts.txt
touch history/history_insert_file.txt
touch history/history_tracking.log

popd
popd

pwd

tree /var/log/tardis

sudo ln -s /var/log/tardis/ /scripts/provenance-logs
sudo ln -s /var/log/tardis/ /provenance-logs

sudo chown -R apache:apache /provenance-logs
sudo chown -R apache:apache /var/log/tardis

ls -lha /var/log/tardis/


