#!/bin/bash
pkill -P $$
n=$1
for ((i=0;i<n;i++));
do
	echo "python3 server.py $i $n"
	xterm -title "server$i" -hold -e "python3 server.py $i $n" &
done