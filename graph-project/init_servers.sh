#!/bin/bash
pkill -P $$
clusters=$1
replicas=3
for ((i=0;i<clusters*replicas;i++));
do
	echo "python3 server.py $i $clusters"
	xterm -title "server$i" -hold -e "python3 server.py $i $clusters" &
done