#!/usr/bin/env python3

import os
import requests
import pygit2
import time
import sys
import importlib  

jenkins_runner = importlib.import_module("arangodb-jenkins-run-pr")
github_comment_tool = importlib.import_module("arangodb-github-post-comment-pr")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

URL = jenkins_runner.create_jenkins_job()

print(URL)
q = input("Do you want to comment this URL on the PR? [Y/n]: ");

if q in ["n", "N"]:
	quit()

github_comment_tool.create_pr_comment(URL)

