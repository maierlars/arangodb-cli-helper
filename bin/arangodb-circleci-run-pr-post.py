#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import http.client
import importlib
import json
import argparse
import itertools

jenkins_runner = importlib.import_module("arangodb-jenkins-run-pr")

def create_circleci_job(params):
    conn = http.client.HTTPSConnection("circleci.com")

    payload = {
        "branch": jenkins_runner.ARANGODB_BRANCH,
        "parameters": params,
    }

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


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--param', '-p', nargs=2, action='append', default=[], help=
"""\
Additional parameters for the job. E.g.:
    --param sanitizer alubsan
    --param nightly true
    --param replication-two true
""")
# --interactive is unused here, but needed for compatibility with adb jenkins
parser.add_argument('--interactive', dest='interactive', choices=['yes', 'no'],
                    nargs='?', default='yes', const='yes')

args = parser.parse_args()
params = dict(map((lambda x: (x[0], x[1])), args.param))

create_circleci_job(params)
