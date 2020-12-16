sudo apt update
sudo apt install python3-pip
sudo pip3 install -r requirements.txt
sudo nohup python3 server.py &
sudo nohup python3 client.py &