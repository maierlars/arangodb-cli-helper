# arangodb-cli-helper
Some random collection of scripts to make the daily work with the arangodb codebase more enjoyable.

Add the `bin/` directory to your PATH, and export the following environment
variables, which are hopefully self-explanatory:

```
ADB_JENKINS_USER
ADB_JENKINS_TOKEN
ADB_GITHUB_USER
ADB_GITHUB_TOKEN
ADB_SLACK_USER
ADB_CIRCLECI_TOKEN
```

To get bash completion, call

```
source path-to-here/bash-completion.bash
```

in your `~/.bashrc`.

There is an (optional) environment variable `ADB_JENKINS_START_OPTS` in order to
pass default parameters to `adb jenkins start`. The string will be subject to
bash's command substitution, arithmetic expansion, word splitting, and pathname
expansion.

`adb circleci start` triggers the CircleCI pipeline named `testing` (override
with `ADB_CIRCLECI_PIPELINE`) of arangodb/arangodb on the current branch. The
pipeline definition id is looked up by name, which requires a new-format
CircleCI API token; alternatively, set `ADB_CIRCLECI_PIPELINE_DEFINITION_ID` to
the id shown in Project Settings > Pipelines.
