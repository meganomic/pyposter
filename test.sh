#!/bin/sh
# Simple script to enable/disable uploading.
# Useful for testing

if [ "$1" == "enable" ]
then
	sed -i -- 's/\t\tusenetserver.post(article)/\t\t#usenetserver.post(article)/g' pyposter.py
	sed -i -- 's/\tusenetserver.connect()/\t#usenetserver.connect()/g' pyposter.py
	sed -i -- 's/\tusenetserver.quit()/\t#usenetserver.quit()/g' pyposter.py

elif [ "$1" == "disable" ]
then
	sed -i -- 's/\t\t#usenetserver.post(article)/\t\tusenetserver.post(article)/g' pyposter.py
	sed -i -- 's/\t#usenetserver.connect()/\tusenetserver.connect()/g' pyposter.py
	sed -i -- 's/\t#usenetserver.quit()/\tusenetserver.quit()/g' pyposter.py

else
	echo -e "Usage: test enable/disable"
fi
