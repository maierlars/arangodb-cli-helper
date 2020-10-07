#!/bin/bash

case $1 in
	jenkins)
		arangodb-jenkins-run-pr-post.py
		;;
	*)
		echo "Unknown command $1"
		;;
esac