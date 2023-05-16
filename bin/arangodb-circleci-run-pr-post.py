#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import http.client
import importlib
import json

jenkins_runner = importlib.import_module("arangodb-jenkins-run-pr")
jenkins_job_manager = importlib.import_module("arangodb-jenkins-get-status")
github_comment_tool = importlib.import_module("arangodb-github-post-comment-pr")
github_comment_lister = importlib.import_module("arangodb-github-list-comments")

def create_circleci_job():
    conn = http.client.HTTPSConnection("circleci.com")
    payload = {"branch": jenkins_runner.ARANGODB_BRANCH}

    headers = {
        'content-type': "application/json",
        'Circle-Token': os.environ['ADB_CIRCLECI_TOKEN']
    }

    conn.request("POST", "/api/v2/project/gh/arangodb/arangodb/pipeline", json.dumps(payload), headers)

    res = conn.getresponse()
    data = res.read()
    jsondata = json.loads(data.decode("utf-8"))
    print("https://app.circleci.com/pipelines/github/arangodb/arangodb/{}".format(jsondata["number"]))

jenkins_runner.check_branches_up_to_date()

create_circleci_job()