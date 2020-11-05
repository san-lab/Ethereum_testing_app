#!/bin/bash
#tmux new-session -d -s my_session './python3 akv_ethereum_signing.py 100 deploy santander https://rinkeby.infura.io/v3/f2a8581c640340758bead17199084148'

session="work"

# set up tmux
tmux start-server

# create a new tmux session, starting vim from a saved session in the new window
tmux new-session -d -s $session

# Select pane 1, set dir to api, run vim
tmux selectp -t 1

# Split pane 1 horizontal by 50%
tmux splitw -h -p 50

# Select pane 2 
tmux selectp -t 2
# Split pane 2 vertically by 50%
tmux splitw -v -p 50

# select pane 0, set to api root
tmux selectp -t 0

# Split pane 3 vertically by 50%
tmux splitw -v -p 50

tmux selectp -t 0
tmux send-keys "python3 akv_ethereum_signing.py 100 deploy santander https://rinkeby.infura.io/v3/9ea72ad9a72d483bb72c005a65022b64" C-m 

tmux selectp -t 1
tmux send-keys "python3 akv_ethereum_signing.py 100 deploy bbva https://rinkeby.infura.io/v3/9ea72ad9a72d483bb72c005a65022b64" C-m 

tmux selectp -t 2
tmux send-keys "python3 akv_ethereum_signing.py 100 deploy bankia https://rinkeby.infura.io/v3/9ea72ad9a72d483bb72c005a65022b64" C-m 

tmux selectp -t 3
tmux send-keys "python3 akv_ethereum_signing.py 100 deploy test https://rinkeby.infura.io/v3/9ea72ad9a72d483bb72c005a65022b64" C-m 

# Finished setup, attach to the tmux session!
tmux attach-session -t $session
