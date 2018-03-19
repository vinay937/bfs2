#!/bin/bash

echo "Running git commit. Please enter commit description below"
bash commit.sh

echo  -ne "|▇▇▇▇▇▇▇▇▇▇                    | (30%)" \\r
sleep 1
echo  -ne "|▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇          | (60%)" \\r
sleep 1
echo  "|▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ | (100%)"
echo "Connected to remote server"
sleep 1
echo "Establishing secure connection 🔒"
sleep 2

ssh -p 2722 devx@128.199.250.218 "bash deploy.bash"
