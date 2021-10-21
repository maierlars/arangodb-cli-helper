#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import requests
import pygit2
import time
import sys
import importlib
from datetime import datetime

jenkins_runner = importlib.import_module("arangodb-jenkins-get-status")
github_comment_tool = importlib.import_module("arangodb-github-list-comments")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def watch_jenkins_status():

    last_run = github_comment_tool.get_latest_jenkins_run()

    if last_run is None:
        eprint("No jenkins runs found")
        quit()

    print("Watching status of last run: {}".format(last_run))

    known_status = dict()

    while True:
        job = jenkins_runner.jenkins_job_status(last_run)

        for sj in job["subBuilds"]:
            do_print = False
            if not sj["jobName"] in known_status:
                do_print = True
            elif known_status[sj["jobName"]] != sj["result"]:
                do_print = True

            known_status[sj["jobName"]] = sj["result"]
            if do_print:
                print("{date} {name}: {result}".format(date = datetime.now().isoformat(timespec = "seconds"),
                    name=sj["jobName"], result=jenkins_runner.result_to_string(sj)))



        if job["result"] is not None:
            print("Job completed. Overall status:")
            jenkins_runner.print_job_status(job)
            quit()

        time.sleep(2)

if __name__ == '__main__':
    try:
        watch_jenkins_status()
    except KeyboardInterrupt:
        pass
