Working Flow Architecture of This Program is:

(./edge_program.png)

The Project Contains two main program, 
  1. (./client.py) as Edge Program.
  2. (./server.py) as HTTP Server Program.
  
 It also contains (./message_count.py) program, which returns the count of successful and buffered messages at any point of time.
 
 Running of this whole program can be done by one command:
  __sudo sh run.sh__
  1. It installs all the dependencies mentioned in the (./requirements.txt) file.
  2. Then it installs & runs the open source dependency i.e. Redis DB needed for the project by launching the (./redis_installation.sh) file.
  3. Finally, It runs the (./server.py) and (./client.py) programs, while server is an Flask HTTP based server running on localhost, port = 5001.
