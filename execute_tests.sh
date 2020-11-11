#!/bin/bash
session="tests1"

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
tmux send-keys "python3 akv_ethereum_signing.py deploy 100 akv santander http://52.157.68.69:8545" C-m 

tmux selectp -t 1
tmux send-keys "python3 akv_ethereum_signing.py deploy 100 akv bbva http://40.68.120.93:8545" C-m 

tmux selectp -t 2
tmux send-keys "python3 akv_ethereum_signing.py deploy 100 akv bankia http://13.80.45.53:8545" C-m 

tmux selectp -t 3
tmux send-keys "python3 akv_ethereum_signing.py deploy 100 akv test http://52.166.19.166:8545" C-m 

# Finished setup, attach to the tmux session!
tmux attach-session -t $session
