echo 'setting up user: 'player$1
echo "with password: $2"

#create a user and add it to the moderator player
#sudo echo -e "$2\n$2\nplayer$1\n\n\n\n\nY\n` | sudo adduser player$1 
sudo /usr/sbin/useradd -c player$1 -m -k/dev/null -s /bin/bash player$1
sudo echo "player$1:$2" | sudo chpasswd player$1
sudo usermod -a -G player$1 moderator

#create directory for user to server communication
sudo mkdir /home/moderator/pipes/$1'tosD'
sudo chown player$1 /home/moderator/pipes/$1'tosD'
sudo chgrp player$1 /home/moderator/pipes/$1'tosD'
sudo chmod 350 /home/moderator/pipes/$1'tosD'

#create directory for server to user communication
sudo mkdir /home/moderator/pipes/'sto'$1'D'
sudo chown player$1 /home/moderator/pipes/'sto'$1'D'
sudo chgrp player$1 /home/moderator/pipes/'sto'$1'D'
sudo chmod 530 /home/moderator/pipes/'sto'$1'D'

#create respective fifos
sudo mkfifo /home/moderator/pipes/sto$1D/sto$1
sudo chmod 530 /home/moderator/pipes/sto$1D/sto$1
sudo mkfifo /home/moderator/pipes/$1tosD/$1tos
sudo chmod 350 /home/moderator/pipes/$1tosD/$1tos

#setup fifo perms
sudo chown player$1 /home/moderator/pipes/sto$1D/sto$1
sudo chown player$1 /home/moderator/pipes/$1tosD/$1tos
sudo chgrp player$1 /home/moderator/pipes/sto$1D/sto$1
sudo chgrp player$1 /home/moderator/pipes/$1tosD/$1tos
sudo chown player$1 /home/moderator/pipes/sto$1D
sudo chown player$1 /home/moderator/pipes/$1tosD
sudo chgrp player$1 /home/moderator/pipes/sto$1D
sudo chgrp player$1 /home/moderator/pipes/$1tosD

#add files to the new user's home directory
sudo cp client.py /home/player$1
sudo cp communication.py /home/player$1
sudo chmod 700 /home/player$1/client.py
sudo chmod 700 /home/player$1/communication.py
sudo chown player$1 /home/player$1/client.py
sudo chgrp player$1 /home/player$1/client.py
sudo chown player$1 /home/player$1/communication.py
sudo chgrp player$1 /home/player$1/communication.py
