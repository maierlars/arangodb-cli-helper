#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import requests
import pygit2
import time
import sys

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

def list_all_prs():
    arangodb_prs_reponse = requests.get(os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "pulls"), auth=(USER, GITHUB_API_TOKEN),
        params={"head": "{}:{}".format(REPO_USER, ARANGODB_BRANCH)})

    if arangodb_prs_reponse.status_code != 200:
            eprint("Failed to get PRs:", arangodb_prs_reponse.reason)
            sys.exit(1)

    arangodb_prs = arangodb_prs_reponse.json()

    if len(arangodb_prs) == 0:
        eprint("PR not found")
        sys.exit(1)


    for pr in arangodb_prs:
        eprint("#{pr[number]} {pr[title]} [{pr[html_url]}]".format(pr=pr))


def create_pr_comment(comment):

    arangodb_prs_reponse = requests.get(os.path.join(GITHUB_BASE_URL, "repos", ARANGODB_REPO, "pulls"), auth=(USER, GITHUB_API_TOKEN),
        params={"head": "{}:{}".format(REPO_USER, ARANGODB_BRANCH)})

    if arangodb_prs_reponse.status_code != 200:
            eprint("Failed to get PRs:", arangodb_prs_reponse.reason)
            sys.exit(1)

    arangodb_prs = arangodb_prs_reponse.json()

    if len(arangodb_prs) == 0:
        eprint("PR not found")
        sys.exit(1)

    if len(arangodb_prs) > 1:
        eprint("found multiple PRs:")
        for pr in arangodb_prs:
            eprint("#{pr[number]} {pr[title]} [{pr[html_url]}]".format(pr=pr))
        sys.exit(1)

    this_pr = arangodb_prs[0]

    comments_url = this_pr["comments_url"]
    print("Commenting on #{pr[number]} {pr[title]}: `{msg}`".format(pr=this_pr, msg=comment))
    post_response = requests.post(comments_url, auth=(USER, GITHUB_API_TOKEN), json={"body": comment})
    if post_response.status_code != 201:
            eprint("Failed to create comment:", post_response.reason)
            sys.exit(1)

    post = post_response.json()
    print(post["html_url"])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        eprint("expected one parameter command")
        sys.exit(1)
    if sys.argv[1] == "comment":
        if len(sys.argv) != 3:
            eprint("expected one parameter with comment content")
            sys.exit(1)
        create_pr_comment(sys.argv[2])
    elif sys.argv[1] == "prs":
        list_all_prs()
    else:
        eprint("unknown command")
        sys.exit(1)
