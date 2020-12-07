#!/usr/bin/env python3

import os
import requests
import pygit2
import time
import sys

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
except KeyError as key:
    print(f"Environment variable missing: {key}")
    sys.exit(1)
except:
    pass

JENKINS_URL="https://jenkins.arangodb.biz"
JOB_NAME="arangodb-matrix-pr"

enterprise_path = os.path.join(os.getcwd(), "enterprise")

ARANGODB_BRANCH = pygit2.Repository(os.getcwd()).head.shorthand
ENTERPRISE_BRANCH = pygit2.Repository(enterprise_path).head.shorthand if os.path.isdir(enterprise_path) else None

OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def result_to_string(job):
    def translate_result(result):
        if result is None:
            return OKCYAN + "Pending..." + ENDC
        elif result == "SUCCESS":
            return OKGREEN + result + ENDC
        elif result == "ABORTED":
            return WARNING + result + ENDC
        else:
            return FAIL + result + ENDC
    return translate_result(job["result"])

def jenkins_job_status(id):
    job_url = os.path.join(JENKINS_URL, "job/{name}/{id}/api/json".format(name=JOB_NAME, id=id))
    job_response = requests.get(job_url, auth=(USER, TOKEN), verify=False)

    if job_response.status_code != 200:
        eprint("Failed to get job:", job_response.reason);
        return None

    job = job_response.json()
    return job

def print_job_status(job):
    print("Description: {description}".format(**job));
    print("Status: {}".format(result_to_string(job)))

    for sj in job["subBuilds"]:
        print("{name}: {result}".format(name=sj["jobName"], result=result_to_string(sj)))

    print("Inspect job here: {url}".format(**job))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        eprint("expected one parameter with job id")
        sys.exit(1)
    job = jenkins_job_status(sys.argv[1])
    if not job is None:
        print_job_status(job)
    sys.exit(0)
