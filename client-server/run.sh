sudo apt update
sudo apt install python3-pip
sudo pip3 install -r requirements.txt
sudo sh redis_installation.sh
sudo nohup python3 server.py &
sudo nohup python3 client.py &