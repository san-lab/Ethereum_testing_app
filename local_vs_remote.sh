#!/bin/bash
session="tests2"

# set up tmux
tmux start-server

# create a new tmux session, starting vim from a saved session in the new window
tmux new-session -d -s $session

# Select pane 1, set dir to api, run vim
tmux selectp -t 1

# Split pane 1 horizontal by 50%
tmux splitw -h -p 50

tmux selectp -t 0
tmux send-keys "python3 akv_ethereum_signing.py deploy 10000 akv santander http://52.157.68.69:8545" C-m 

tmux selectp -t 1
tmux send-keys "python3 akv_ethereum_signing.py deploy 10000 local bbva http://40.68.120.93:8545" C-m 

# Finished setup, attach to the tmux session!
tmux attach-session -t $session
