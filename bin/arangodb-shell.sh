#!/bin/bash


function usage {
    cat <<USAGE
Usage: $0 [-h|--help] <command> [<args>]
  -h|--help           show this usage information
Commands:
  jenkins start       start a jenkins pr matrix on the current branch
  jenkins status      query the status of the last jenkins pr matrix posted on the PR
  jenkins watch       watch the status of the last jenkins pr matrix posted on the PR
  prs                 list all PRs associated with the current branch
USAGE
}

if [ $# -eq 0 ]
then
    usage
    exit 1
fi


case "$1" in
    jenkins)
        if [ $# -lt 2]; then
            echo "Missing argument to jenkins."
            echo ""
            usage
            exit 1
        fi
        case "$2" in
            start)
                arangodb-jenkins-run-pr-post.py
                ;;
            status)
                arangodb-jenkins-pr-status.py
                ;;
            watch)
                arangodb-jenkins-pr-status-watch.py
                ;;
            *)
                echo "Unknown command or option to $1: $2"
                echo ""
                usage
                exit 0
                ;;
        esac
        ;;
    prs)
        arangodb-github-post-comment-pr.py prs
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown command or option: $1"
        echo ""
        usage
        exit 1
        ;;
esac
