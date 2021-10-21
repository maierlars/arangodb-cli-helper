#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import requests
import pygit2
import time
import sys
import importlib
import argparse

jenkins_runner = importlib.import_module("arangodb-jenkins-run-pr")
jenkins_job_manager = importlib.import_module("arangodb-jenkins-get-status")
github_comment_tool = importlib.import_module("arangodb-github-post-comment-pr")
github_comment_lister = importlib.import_module("arangodb-github-list-comments")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--interactive', dest='interactive', choices=['yes', 'no'],
        nargs='?', default='yes', const='yes')

args = parser.parse_args()



def last_jenkins_run():
    comments = github_comment_lister.list_all_jenkins_pr_comments()
    if len(comments) == 0:
        return None

    if len(comments) > 15:
        print("There are now more then 15 jenkins comments. Consider cleaning some of them.")

    last_run = list(filter(len, comments[-1]["body"].split("/")))[-1]

    print("Fetching status of last run: {}".format(last_run))
    last_job = jenkins_job_manager.jenkins_job_status(last_run)

    return last_job

jenkins_runner.check_branches_up_to_date()

last_run = last_jenkins_run()
if last_run is not None:
    if last_run["result"] is None:
        q = input("Last job is still running, do you want to continue (y) and/or abort (a) it? [A/y/n]: ");
        if q in ["a", "A", ""]:
            jenkins_runner.abort_jenkins_job(last_run["id"])
        elif q in ["y", "Y"]:
            pass
        else:
            quit()
    else:
        print("Job has ended, Status: " + last_run["result"])

URL = jenkins_runner.create_jenkins_job(args)

print(URL)

if args.interactive == 'yes':
    q = input("Do you want to comment this URL on the PR? [y/N]: ");

    if q not in ["y", "Y"]:
        quit()

    github_comment_tool.create_pr_comment(URL)
