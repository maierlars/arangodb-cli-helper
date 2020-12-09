#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import requests
import pygit2
import time
import sys
import importlib

jenkins_runner = importlib.import_module("arangodb-jenkins-get-status")
github_comment_tool = importlib.import_module("arangodb-github-list-comments")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

comments = github_comment_tool.list_all_jenkins_pr_comments()

if len(comments) == 0:
    eprint("No jenkins runs found")
    quit()

last_run = list(filter(len, comments[-1]["body"].split("/")))[-1]

print("Fetching status of last run: {}".format(last_run))

job = jenkins_runner.jenkins_job_status(last_run)
jenkins_runner.print_job_status(job)
