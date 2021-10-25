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

def slurp_version_file():
    try:
        with open("ARANGO-VERSION", "r") as fh:
            return fh.read().strip()
    except:
        with open("VERSION", "r") as fh:
            return fh.read().strip()

def read_base_version():
    str = slurp_version_file()
    parts = re.split('[.-]', str)
    if parts[-1] == 'devel':
        return 'devel'
    else:
        version = '.'.join(parts[0:2])
        return version

arangodb_repo_urls = {
    "community": [
        "git@github.com:arangodb/arangodb.git",
        "https://github.com/arangodb/arangodb.git",
        "git@github.com:arangodb/arangodb",
    ],
    "enterprise": [
        "git@github.com:arangodb/enterprise.git",
        "https://github.com/arangodb/enterprise.git",
        "git@github.com:arangodb/enterprise",
    ],
}

def get_matching_remote(repo, remote_urls):
    remotes = [remote.name for remote in repo.remotes if remote.url
        in remote_urls]
    if 0 == len(remotes):
        eprint("!!! Couldn't find any matching remote in the repository", repo.path)
        eprint("Tried to detect by finding one of the following urls:")
        for url in remote_urls:
            eprint(" -", url)
        eprint("Looked at the following remotes:")
        for remote in repo.remotes:
            eprint(" -", remote.name, "(", remote.url, ")")
        sys.exit(1)

    if 1 < len(remotes):
        eprint("Warning: found multiple arangodb remotes.")
        eprint("Using the first of the following candidates:")
        for remote in remotes:
            eprint(" -", remote)

    return remotes[0]

JENKINS_URL="https://jenkins.arangodb.biz:3456"
JOB_NAME="arangodb-matrix-pr"

community_path = os.getcwd()
enterprise_path = os.path.join(community_path, "enterprise")

repo_community = pygit2.Repository(community_path)
repo_enterprise = pygit2.Repository(enterprise_path)

ARANGODB_BRANCH = repo_community.head.shorthand
ENTERPRISE_BRANCH = repo_enterprise.head.shorthand if os.path.isdir(enterprise_path) else None

BASE_VERSION = read_base_version()

def create_jenkins_job(args):
    if args.interactive == 'yes':
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

def check_branch_up_to_date(repo, remote):
    branch = repo.head.shorthand
    remote_branch = '/'.join(["refs", "remotes", remote, branch])
    local_rev = repo.head.target
    remote_rev = repo.revparse_single(remote_branch).oid
    merge_base = repo.merge_base(local_rev, remote_rev)
    # Check that we don't have local commits that aren't pushed.
    # Remote commits we know of that aren't merged into our local branch
    # are fine, though.
    return merge_base == local_rev


def check_branches_up_to_date():
    community_remote = get_matching_remote(repo_community,
            arangodb_repo_urls["community"])
    enterprise_remote = get_matching_remote(repo_enterprise,
            arangodb_repo_urls["enterprise"])
    com_up_to_date = check_branch_up_to_date(repo_community, community_remote)
    ent_op_to_date = check_branch_up_to_date(repo_enterprise, enterprise_remote)
    if not com_up_to_date:
        eprint("Community branch has unpublished commits")
    if not ent_op_to_date:
        eprint("Enterprise branch has unpublished commits")
    if not com_up_to_date or not ent_op_to_date:
        sys.exit(1)

if __name__ == '__main__':
    check_branches_up_to_date()

    url = create_jenkins_job()
    print(url)
    sys.exit(0)
