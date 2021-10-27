#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import requests
import pygit2
import time
import sys
import re

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

try:
    USER = os.environ['ADB_GITHUB_USER']
    GITHUB_API_TOKEN = os.environ['ADB_GITHUB_TOKEN']
except KeyError as key:
    print(f"Environment variable missing: {key}")
    sys.exit(1)
except:
    pass

GITHUB_BASE_URL = "https://api.github.com/"
REPO_USER = "arangodb"

ARANGODB_REPO = "arangodb/arangodb"
ENTERPRISE_REPO = "arangodb/enterprise"

enterprise_path = os.path.join(os.getcwd(), "enterprise")

ARANGODB_BRANCH = pygit2.Repository(os.getcwd()).head.shorthand
ENTERPRISE_BRANCH = pygit2.Repository(enterprise_path).head.shorthand if os.path.isdir(enterprise_path) else None

def get_pr_comments():
    arangodb_prs_reponse = requests.get(os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "pulls"), auth=(USER, GITHUB_API_TOKEN),
        params={"head": "{}:{}".format(REPO_USER, ARANGODB_BRANCH)})

    if arangodb_prs_reponse.status_code != 200:
        eprint("Failed to get PR:", arangodb_prs_reponse.reason)
        sys.exit(1)

    arangodb_prs = arangodb_prs_reponse.json()

    if len(arangodb_prs) == 0:
        eprint("PR not found")
        return []

    if len(arangodb_prs) > 1:
        eprint("found multiple PRs:")
        for pr in arangodb_prs:
            eprint("#{pr[number]} {pr[title]} [{pr[html_url]}]".format(pr=pr))
        sys.exit(1)

    this_pr = arangodb_prs[0]

    comments_url = this_pr["comments_url"] + "?per_page=100"
    if len(comments_url) > 90:
        print("WARNING: There are more than 90 PR comments. Consider cleaning up some jenkins runs.")

    comments_response = requests.get(comments_url, auth=(USER, GITHUB_API_TOKEN))
    if comments_response.status_code != 200:
        eprint("Failed to get comment list:", comments_response.reason, comments_response.status_code)
        sys.exit(1)

    comments = comments_response.json()
    return comments

def list_all_jenkins_pr_comments():

    comments = get_pr_comments()
    jenkins_runs = [c for c in comments if re.match("^https?:\\/\\/jenkins.*$", c["body"]) ]

    return jenkins_runs

def get_latest_jenkins_run_url():
    arangodb_prs_reponse = requests.get(os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "pulls"), auth=(USER, GITHUB_API_TOKEN),
    params={"head": "{}:{}".format(REPO_USER, ARANGODB_BRANCH)})

    if arangodb_prs_reponse.status_code != 200:
        eprint("Failed to get PR:", arangodb_prs_reponse.reason)
        sys.exit(1)

    arangodb_prs = arangodb_prs_reponse.json()

    if len(arangodb_prs) == 0:
        return None

    if len(arangodb_prs) > 1:
        eprint("found multiple PRs:")
        for pr in arangodb_prs:
            eprint("#{pr[number]} {pr[title]} [{pr[html_url]}]".format(pr=pr))
        sys.exit(1)

    status_url = os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "statuses", arangodb_prs[0]["head"]["sha"])

    arangodb_status_reponse = requests.get(status_url, auth=(USER, GITHUB_API_TOKEN))

    if arangodb_prs_reponse.status_code != 200:
        eprint("Failed to get Head Status:", arangodb_prs_reponse.reason)
        sys.exit(1)

    arangodb_status = arangodb_status_reponse.json()

    for status in arangodb_status:
        if status["context"] == "arangodb-matrix-pr":
            return status["target_url"]

    return None

def get_latest_jenkins_run():
    url = get_latest_jenkins_run_url()
    if url is not None:
        return list(filter(len, url.split("/")))[-1]
    return None


def clean_old_jenkins_pr_comments(last = 1):

    jenkins_runs = list_all_jenkins_pr_comments()
    count = len(jenkins_runs)

    print("There are currently {} PR comments, keeping the last {} comments.".format(count, last))

    for r in jenkins_runs:
        count -= 1
        if last is not None and count < last:
            break

        print("deleting comment {}: `{}`".format(r["id"], r["body"]))
        delete_url = os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "issues/comments/", str(r["id"]))
        print(delete_url)

        delete_response = requests.delete(delete_url, auth=(USER, GITHUB_API_TOKEN))
        if delete_response.status_code != 204:
            eprint("Failed to delete comment: ", delete_response.reason, delete_response.status_code)
            sys.exit(1)

if __name__ == '__main__':
    for c in list_all_jenkins_pr_comments():
        print("{created_at}: {body}".format(**c))
