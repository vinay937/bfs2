#!/bin/bash
git add .
desc=$(openssl rand -base64 12)
git commit -m "$desc"
git push origin master
