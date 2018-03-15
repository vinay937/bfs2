#!/bin/bash
git add .
read -p "Commit Discription: " desc
git commit -m "$desc"
git push origin master