#!/bin/bash


function usage {
    cat <<USAGE
Usage: $0 [-h|--help] <command> [<args>]
  -h|--help           show this usage information
Commands:
  jenkins             start a jenkins pr matrix on the current branch
USAGE
}

if [ $# -eq 0 ]
then
    usage
    exit 1
fi


case $1 in
        jenkins)
                arangodb-jenkins-run-pr-post.py
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