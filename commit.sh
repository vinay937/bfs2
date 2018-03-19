#!/bin/bash
git add .
if [ $# -ge 1 ]
then
    desc=$@
else
    desc=$(openssl rand -base64 12)
fi
git commit -m "$desc"
git push origin master
