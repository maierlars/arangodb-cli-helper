#!/usr/bin/env python3
# vim: set et sw=4 sts=4:

import os
import sys
import http.client
import importlib
import json
import argparse

jenkins_runner = importlib.import_module("arangodb-jenkins-run-pr")

PROJECT_SLUG = "gh/arangodb/arangodb"
# Name of the pipeline definition (see CircleCI Project Settings > Pipelines).
PIPELINE_NAME = os.environ.get("ADB_CIRCLECI_PIPELINE", "testing")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def circleci_request(method, path, body=None):
    conn = http.client.HTTPSConnection("circleci.com")
    headers = {
        'content-type': "application/json",
        'Circle-Token': os.environ['ADB_CIRCLECI_TOKEN']
    }
    conn.request(method, "/api/v2" + path, None if body is None else json.dumps(body), headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    try:
        jsondata = json.loads(data)
    except json.JSONDecodeError:
        jsondata = {"message": data}
    return res.status, jsondata

def get_pipeline_definition_id():
    """
    Pipelines are triggered by definition id. It can be set explicitly via
    ADB_CIRCLECI_PIPELINE_DEFINITION_ID, otherwise we look it up by name.
    Note that the lookup endpoint requires a new-format CircleCI API token.
    """
    definition_id = os.environ.get("ADB_CIRCLECI_PIPELINE_DEFINITION_ID")
    if definition_id:
        return definition_id

    status, project = circleci_request("GET", f"/project/{PROJECT_SLUG}")
    if status != 200:
        eprint(f"Failed to get project {PROJECT_SLUG}: {status} {project.get('message')}")
        sys.exit(1)

    status, definitions = circleci_request("GET", f"/projects/{project['id']}/pipeline-definitions")
    if status != 200:
        eprint(f"Failed to list pipeline definitions: {status} {definitions.get('message')}")
        eprint(f"Either create a new-format CircleCI API token, or set ADB_CIRCLECI_PIPELINE_DEFINITION_ID")
        eprint(f"to the id of the '{PIPELINE_NAME}' pipeline (see Project Settings > Pipelines).")
        sys.exit(1)

    matching = [d for d in definitions.get("items", []) if d.get("name") == PIPELINE_NAME]
    if len(matching) != 1:
        eprint(f"Expected exactly one pipeline definition named '{PIPELINE_NAME}', found:")
        for d in definitions.get("items", []):
            eprint(" -", d.get("name"), "(", d.get("id"), ")")
        sys.exit(1)
    return matching[0]["id"]

def create_circleci_job(params):
    payload = {
        "definition_id": get_pipeline_definition_id(),
        "config": {"branch": jenkins_runner.ARANGODB_BRANCH},
        "checkout": {"branch": jenkins_runner.ARANGODB_BRANCH},
        "parameters": params,
    }

    status, jsondata = circleci_request("POST", f"/project/{PROJECT_SLUG}/pipeline/run", payload)

    if status == 201:
        print("https://app.circleci.com/pipelines/github/arangodb/arangodb/{}".format(jsondata["number"]))
    elif status == 200:
        # Successful response, but no pipeline was created
        eprint("No pipeline created:", jsondata.get("message"))
        sys.exit(1)
    else:
        eprint(f"Failed to trigger pipeline: {status} {jsondata.get('message', jsondata)}")
        sys.exit(1)

def castParam(argp, param, arg):
    def toString(arg):
        return str(arg)
    def toInt(arg):
        return int(arg)
    def toBool(arg):
        if arg.lower() in ["true", "yes", "on", "1"]:
            return True
        if arg.lower() in ["false", "no", "off", "0"]:
            return False
        raise argparse.ArgumentError(argp, f"Invalid boolean value for {param}: {arg}")
    # This list isn't complete, and we don't verify the argument.
    switch = {
            'dont-cancel-pipelines': toBool,
            'enterprise-branch': toString,
            'without-instrumentation': toBool,
            'with-tsan': toBool,
            'with-alubsan': toBool,
            'full': toBool,
            # TODO maybe make this an array parameter for a nicer api and auto
            # completion?
            'config-definitions': toString,
            'replication-two': toBool,
    }
    if param not in switch:
        raise argparse.ArgumentError(argp, f"Unknown job param {param}")
    return switch[param](arg)

jenkins_runner.check_branches_up_to_date()

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
# If at some point maintaining the arguments here gets in the way, I suggest
# to add --param.string, --param.bool and possibly --param.number; that way we
# can pass arbitrary arguments, but still get the JSON type right so CircleCI
# doesn't complain.
argp = parser.add_argument('--param', '-p', nargs=2, action='append', default=[], help=
"""\
Additional parameters for the job. E.g.:
    --param dont-cancel-pipelines true
    --param enterprise-branch devel
    --param with-alubsan true
    --param with-tsan true
    --param without-instrumentation false
    --param full true
    --param config-definitions 'tests.yml ui.yml'
    --param replication-two true
By default, enterprise-branch is set to the branch checked out in ./enterprise.
""")
# --interactive is unused here, but needed for compatibility with adb jenkins
parser.add_argument('--interactive', dest='interactive', choices=['yes', 'no'],
                    nargs='?', default='yes', const='yes')

args = parser.parse_args()
# convert params to dict
params = dict(map((lambda x: (x[0], x[1])), args.param))

# convert params to the appropriate type, or throw on unknown parameters
try:
    params = {k: castParam(argp, k, v) for k, v in params.items()}
except argparse.ArgumentError as e:
    parser.error(str(e))

if 'enterprise-branch' not in params and jenkins_runner.ENTERPRISE_BRANCH is not None:
    params['enterprise-branch'] = jenkins_runner.ENTERPRISE_BRANCH

create_circleci_job(params)
