#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import pygit2
import re
import requests
import sys
import time

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

try:
    import urllib3
    urllib3.disable_warnings()
except:
    pass

try:
    USER = os.environ['ADB_JENKINS_USER']
    TOKEN = os.environ['ADB_JENKINS_TOKEN']
    SLACK_USER = os.environ['ADB_SLACK_USER']
except KeyError as key:
    print(f"Environment variable missing: {key}")
    sys.exit(1)
except:
    pass

def read_base_version():
    with open("VERSION", "r") as fh:
        str = fh.read().strip()
    parts = re.split('[.-]', str)
    if parts[-1] == 'devel':
        return 'devel'
    else:
        version = '.'.join(parts[0:2])
        return version

JENKINS_URL="https://jenkins.arangodb.biz"
JOB_NAME="arangodb-matrix-pr"

community_path = os.getcwd()
enterprise_path = os.path.join(community_path, "enterprise")

repo_community = pygit2.Repository(community_path)
repo_enterprise = pygit2.Repository(enterprise_path)

ARANGODB_BRANCH = repo_community.head.shorthand
ENTERPRISE_BRANCH = repo_enterprise.head.shorthand if os.path.isdir(enterprise_path) else None

BASE_VERSION = read_base_version()

def create_jenkins_job():
    confirm = input("Run jenkins on {b}, enterprise {eb}:\nContinue? [Y/n] ".format(b=ARANGODB_BRANCH, eb=ENTERPRISE_BRANCH))
    if confirm.strip() not in ["Y", "y", ""]:
        sys.exit(1)

    params = {
        "BASE_VERSION": BASE_VERSION,
        "ARANGODB_BRANCH": ARANGODB_BRANCH,
        "CHECK_API": False,
    }
    if not ENTERPRISE_BRANCH is None:
        params["ENTERPRISE_BRANCH"] = ENTERPRISE_BRANCH

    if not SLACK_USER is None:
        params["SLACK"] = SLACK_USER

    create_response = requests.post(os.path.join(JENKINS_URL, "job/{}/buildWithParameters".format(JOB_NAME)),
        auth=(USER, TOKEN), params=params, verify=False)

    if create_response.status_code != 201:
        eprint("Failed to create job:", create_response.reason);
        sys.exit(1)
    eprint("Job queued. Waiting for it to start.")

    queue_url = create_response.headers["Location"]

    counter = 0
    while True:
        queue_reponse = requests.get(os.path.join(queue_url, "api/json"), auth=(USER, TOKEN), verify=False)
        if queue_reponse.status_code != 200:
            eprint("Failed to get queue entry:", queue_reponse.reason)
            sys.exit(1)
        response = queue_reponse.json()

        if "cancelled" in response and response["cancelled"]:
            eprint("Job cancelled")
            sys.exit(1)

        if "executable" in response:
            return response["executable"]["url"]

        time.sleep(1)
        counter += 1
        if counter % 4 == 0:
            eprint("Waiting for job to start...")

def abort_jenkins_job(id):

    job_url = os.path.join(JENKINS_URL, "job/{name}/{id}/stop".format(name=JOB_NAME, id=id))
    job_response = requests.post(job_url, auth=(USER, TOKEN), verify=False)

    if job_response.status_code != 200:
        eprint("Failed to abort job:", job_response.reason);
        sys.exit(1)
    print("{} aborted".format(id))


if __name__ == '__main__':
    url = create_jenkins_job()
    print(url)
    sys.exit(0)
