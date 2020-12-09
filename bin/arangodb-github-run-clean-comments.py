#!/usr/bin/env python3

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

confirm = input("Do you want to clean old jenkins pr comments? [Y/n]: ");
if confirm.strip() not in ["Y", "y", ""]:
        sys.exit(1)

github_comment_tool.clean_old_jenkins_pr_comments()
