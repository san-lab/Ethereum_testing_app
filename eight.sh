#!/bin/bash
session="tests4"

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

# select pane 0, set to api root
tmux selectp -t 0

# Split pane 3 vertically by 50%
tmux splitw -v -p 50

# select pane 0, set to api root
tmux selectp -t 2

# Split pane 3 vertically by 50%
tmux splitw -v -p 50

# select pane 0, set to api root
tmux selectp -t 4

# Split pane 3 vertically by 50%
tmux splitw -v -p 50

# select pane 0, set to api root
tmux selectp -t 6

# Split pane 3 vertically by 50%
tmux splitw -v -p 50

# Finished setup, attach to the tmux session!
tmux attach-session -t $session

