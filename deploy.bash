#!/bin/bash

bash commit.bash

ssh -p 2722 devx@128.199.250.218 "sudo bash deploy.bash"

