sudo apt install python2
sudo adduser moderator
sudo cp -r ./* /home/moderator
sudo chmod a+x /home/moderator
sudo chmod 711 /home/moderator/pipes
sudo touch /home/moderator/log/dummy-m.log
sudo chown moderator /home/moderator/log/*
sudo chgrp moderator /home/moderator/log/*
sudo chown moderator /home/moderator/*
sudo chgrp moderator /home/moderator/*
sudo chmod 700 /home/moderator/log/template
sudo chmod 700 /home/moderator/log/dummy-m.log
python2 makeusers.py 16
